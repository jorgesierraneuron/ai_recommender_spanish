import json
from bson.json_util import dumps
from app.config.config import MongoConfig
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection
from pprint import PrettyPrinter
from dotenv import load_dotenv, find_dotenv
from typing import Dict
import threading
import os 



class MongoManager(): 
    
    _lock = threading.Lock()
    _instance = None
    printer = PrettyPrinter()
    load_dotenv(find_dotenv())
    _collections : Dict[str, Collection] = {}
    _collection : Collection = None
    
    # Singleton pattern
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MongoManager, cls).__new__(cls)
                cls._instance.__initialized = False
            return cls._instance

    def __init__(self) -> None:
        
        self.__username = MongoConfig.username.value #os.environ['MONGODB_USER']
        self.__password = MongoConfig.password.value #os.environ['MONGO_DB_PASSWORD']
        self.__cluster_name = MongoConfig.cluster_name.value #os.environ['MONGODB_CLUSTER_NAME']
        self.__uri = f"mongodb+srv://{self.__username}:{self.__password}@{self.__cluster_name}.pmrntt9.mongodb.net/?retryWrites=true&w=majority"

        self.client = MongoClient(self.__uri, server_api=ServerApi('1'))

    def select_collection(self, database_name:str, collection_name: str):
        if collection_name in self._collections:
            self._collection = self._collections[collection_name]
        else:
            self._collection = self.client[database_name][collection_name]
            self._collections[collection_name] = self._collection
        return self._collection

    
    # def last_message(self, conversation_id): 

    #     result_pre = list(self._collection.aggregate(
    #                 [
                        
    #                     {"$match": {"chat_id": conversation_id}},
                        
    #                     {
    #                         "$group": {
    #                             "_id": "$chat_id",
    #                             "maxNumeroConversacion": {"$max": "$message_number"}
    #                         }
    #                     }
    #                     ]
    #                     ))
        
    #     if result_pre:
    #         result_pre = result_pre[0]
    #         final_result = list(self._collection.aggregate(
    #             [
    #                 {"$match": {"$and": [{"chat_id": result_pre['_id']}, {"message_number": result_pre['maxNumeroConversacion']}]}}
    #             ]
    #         ))
        
    #         return final_result[0]
        
    #     else: 
    #         return 'Not finded'

    def get_message_chat_id(self,chat_id): 
        try: 
            result = self._collection.find_one({"chat_id": chat_id})
        except Exception as e: 
            raise e
        
        if result:
            return json.loads(dumps(result))
        else:
            return 'Not finded'
    
    def save_message(self,data, chat_id ): 
        
        try: 
            self._collection.update_one({"chat_id": chat_id}, {"$set": data},upsert=True)
        except Exception as e:
            raise e
        return 'Success' 
    



         
        