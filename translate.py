from groq import Groq
import textwrap
from fpdf import FPDF
import tiktoken
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
import yaml
from langchain_community.document_loaders import PyPDFLoader
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import glob
import os
import re 

load_dotenv()
client = Groq()

def remove_emoji(string):
    emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', string)

def string_to_txt(text, path): 
     with open(path, "w") as text_file:
        text_file.write(text)

def tiktoken_len(text):
        """
        Function that estimate the number of tokens
        """
        tokenizer = tiktoken.get_encoding('cl100k_base')
        tokens =  tokenizer.encode(
            text,
            disallowed_special=()
        )
        return len(tokens)

def chunkSplitter(chunksize,overlap,data):

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunksize,
            chunk_overlap=overlap,  # number of tokens overlap between chunks
            length_function=tiktoken_len,
            separators=['\n\n', '\n', ' ', '']
            )

        chunks = text_splitter.split_text(data)
        return chunks

def read_yaml_file():
        file_path = 'app/config.yaml'
        try:
            with open(file_path, 'r') as file:
                data = yaml.safe_load(file)
            return data
        except FileNotFoundError:
            print(f"Error: File '{file_path}' not found.")
            return None
        except yaml.YAMLError as e:
            print(f"Error reading YAML file: {e}")
            return None
        
def pdfLoader(path):
        """
        Load data from PDF file 
        """
        loader = PyPDFLoader(path)
        pages = loader.load_and_split()
        return pages

def text_to_pdf(text, filename):
    a4_width_mm = 210
    pt_to_mm = 0.35
    fontsize_pt = 10
    fontsize_mm = fontsize_pt * pt_to_mm
    margin_bottom_mm = 10
    character_width_mm = 7 * pt_to_mm
    width_text = a4_width_mm / character_width_mm

    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(True, margin=margin_bottom_mm)
    pdf.add_page()
    pdf.set_font(family='Courier', size=fontsize_pt)
    splitted = text.split('\n')

    for line in splitted:
        lines = textwrap.wrap(line, width_text)

        if len(lines) == 0:
            pdf.ln()

        for wrap in lines:
            pdf.cell(0, fontsize_mm, wrap, ln=1)

    pdf.output(filename, 'F')

def string_to_pdf(text, file_path):
    """
    Converts a given string to a PDF file and saves it locally.

    Parameters:
    text (str): The string to be written to the PDF.
    file_path (str): The path where the PDF file will be saved.

    Returns:
    None
    """
    # Create a canvas object with the specified file path and page size
    c = canvas.Canvas(file_path, pagesize=letter)
    
    # Set up some basic properties
    width, height = letter
    c.setFont("Helvetica", 12)

    # Split the text into lines
    lines = text.split('\n')

    # Define the starting position
    x, y = 50, height - 50

    # Add the text to the PDF, line by line
    for line in lines:
        c.drawString(x, y, line)
        y -= 15  # Move to the next line (adjust the spacing as needed)

        # Check if we need to create a new page
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - 50

    # Save the PDF
    c.save()

    print(f'Saved file: {file_path}')

def files_paths(ruta_carpeta, extension="pdf"):
    """
    Imprime las rutas de todos los archivos en una carpeta especificada con una extensión dada.
    
    Parámetros:
    ruta_carpeta (str): Ruta de la carpeta donde se encuentran los archivos.
    extension (str): Extensión de los archivos a imprimir, por defecto se imprimirán todas las rutas de archivos.
    """
    archivos = glob.glob(os.path.join(ruta_carpeta, f"*.{extension}"))
    
    return archivos


def pdf_text(path):
    data = pdfLoader(path)

    return data


def format_user_text(text):
    user_text = "please translate this text -> {context}"

    user_text = user_text.format(context = text)

    return user_text

def translate(user_text):


    chat_completion = client.chat.completions.create(
        
        messages=[
            {
                "role": "system",
                "content": read_yaml_file()["system_prompt"]
            },
            # Set a user message for the assistant to respond to.
            {
                "role": "user",
                "content": user_text,
            }
        ],
        model="llama3-70b-8192",
        temperature=0.1,
        max_tokens=32768,
        top_p=1,
        stop=None,
        stream=False,
    )

    # Print the completion returned by the LLM.
    

    text = chat_completion.choices[0].message.content

    return text 

    #string_to_pdf(text,'files_spanish/test.pdf')



if __name__ == "__main__":
    for path in files_paths('files'): 
        #path = 'files/Advanced AI Product Management & Leadership Certification2.pdf'
        text_for_pdf = pdf_text(path)

        print(path)
        translated_text =''
        for doc in text_for_pdf: 
            
            chunks = chunkSplitter(10000,0,doc.page_content)
            for chunk in chunks:
                user_text = format_user_text(chunk)
                completion = translate(user_text)
                translated_text += completion

            print(f'translatef text: {len(translated_text)}')        
        
        path_final = 'files_spanish/'+path.split('/')[1].replace('.pdf','.txt')

        text_final = remove_emoji(translated_text)
        #string_to_pdf(translated_text,path_final)     
        string_to_txt(text_final, path_final)


    
                