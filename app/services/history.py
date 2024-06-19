from app.services.mongomanager import MongoManager

# la clase history va a heredar de mongomanager

class history(MongoManager): 

    def __init__(self, ) -> None:
        super().__init__()
        
        
    
    def get_last_message(self, chat_id): 
        response = super().get_message_chat_id(chat_id)
        
        return response #if response=='Not finded' else  response['interaction']
        

    def save_new_message(self, new_message, chat_id): 
        super().save_message(new_message, chat_id)
        