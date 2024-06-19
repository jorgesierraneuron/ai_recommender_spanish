import sys
import os
from dotenv import load_dotenv, find_dotenv
from enum import Enum
import logging

load_dotenv(find_dotenv())


def load_configurations(app):
    load_dotenv()
    app.config["ACCESS_TOKEN"] = os.getenv("ACCESS_TOKEN")
    app.config["YOUR_PHONE_NUMBER"] = os.getenv("YOUR_PHONE_NUMBER")
    app.config["APP_ID"] = os.getenv("APP_ID")
    app.config["APP_SECRET"] = os.getenv("APP_SECRET")
    app.config["RECIPIENT_WAID"] = os.getenv("RECIPIENT_WAID")
    app.config["VERSION"] = os.getenv("VERSION")
    app.config["PHONE_NUMBER_ID"] = os.getenv("PHONE_NUMBER_ID")
    app.config["VERIFY_TOKEN"] = os.getenv("VERIFY_TOKEN")


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )


class MongoConfig(Enum):

    # # for deployment 
    # username = secret['MONGODB_USER']
    # password = secret['MONGO_DB_PASSWORD']
    # cluster_name = secret['MONGODB_CLUSTER_NAME']
    
    username = os.environ['MONGODB_USER']
    password = os.environ['MONGO_DB_PASSWORD']
    cluster_name = os.environ['MONGODB_CLUSTER_NAME']

    
class embeding_config(Enum):
    OPENAI_KEY = os.environ["OPENAI_KEY"]
    QDRANT_API_KEY = os.environ["QDRANT_API_KEY"]
    QDRANT_URL = os.environ.get("QDRANT_URL")
    MODEL = 'text-embedding-3-small'
    COLLECTION = 'ai_recommender_knowledge'