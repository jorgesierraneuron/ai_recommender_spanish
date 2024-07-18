import threading
import asyncio
from collections import deque
import time 
import logging
from flask import current_app, jsonify
import json
import requests
from app.services.llamager import LLamager
from app.config.config import WhatsAppCredentials

# from app.services.openai_service import generate_response
import re

llamager = LLamager()
session_data = {}

def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )

async def process_message(wa_id, name):

    start_time = time.time()
    
    with session_data[wa_id]['lock']:
        if session_data[wa_id]['is_processing']:
            return 
        if not session_data[wa_id]['queue']:
            return 
        session_data[wa_id]['is_processing'] = True 
        message_info = session_data[wa_id]['queue'].popleft() 

    #try: 
    wa_id_message, question = message_info['wa_id'], message_info['question']
    response_ai = llamager.process(question,'user', wa_id_message,name)
    data = get_text_message_input(wa_id,response_ai)
            
    await send_message(data)
    # except:
    #     print('error processing')
    
    with session_data[wa_id]['lock']:
        session_data[wa_id]['is_processing'] = False
        if session_data[wa_id]['queue']:
            asyncio.create_task(process_message(wa_id, name))         

    end_time = time.time()
    print(f'Process time: {end_time-start_time}')
     


async def generate_response(question, wa_id, name):
    # Return text in uppercase
    print('inside generate_response')
    start_time = time.time()

    if wa_id not in session_data:
        session_data[wa_id] = {'queue': deque(), 'lock': threading.Lock(), 'is_processing': False}
    
    session_data[wa_id]['queue'].append({'wa_id': wa_id, 'question': question})
    
    asyncio.create_task(process_message(wa_id, name))
    
    #response_ai = llamager.process(question,'user', wa_id,name)
    #return response_ai


async def send_message(data):
    headers = {
        "Content-type": "application/json",
        #"Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
        "Authorization": f"Bearer {WhatsAppCredentials.access_token.value}",
    }

    #url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    url = f"https://graph.facebook.com/{WhatsAppCredentials.version.value}/{WhatsAppCredentials.phone_number_id.value}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


async def process_whatsapp_message(body):
    print('inside process_whatsapp_message')
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_body = message["text"]["body"]

    # TODO: implement custom function here
    response = await generate_response(message_body, wa_id, name)
    

    # OpenAI Integration
    # response = generate_response(message_body, wa_id, name)
    # response = process_text_for_whatsapp(response)
    
    #data = get_text_message_input(wa_id, response)
    
    #send_message(data)


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )
