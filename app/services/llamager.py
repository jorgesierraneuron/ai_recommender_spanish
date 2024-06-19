import yaml
from app.services.history import history
from app.services.AbstractClasses.abstractClasses import QdrantRag, PromptFormatter, textFormat
from app.services.qdrant_manager import qdrant_manager
from app.config.config import embeding_config
import time
from dotenv import load_dotenv
from groq import (
    Groq,
    AsyncGroq
)

load_dotenv()


class LLamager:
    
    qdrant = qdrant_manager(embeding_config.QDRANT_URL.value,embeding_config.QDRANT_API_KEY.value)
    History = history()
    History.select_collection('ai_recommender','chats')
    rag_qdrant = QdrantRag(qdrant)
    
    def __init__(self,) -> None:
        self.model = 'llama3-70b-8192'
        self.rag_model = embeding_config.MODEL.value
        self.collection_name = embeding_config.COLLECTION.value
        self.validator_model = 'llama3-8b-8192'
        self.temperature = 0.5,
        self.max_tokens = 1024,
        self.stop = None,
        self.stream = False,
        self.client = Groq()
        #self.messages = self.get_system_prompt("system_prompt")

    
    def __rag(self, interaction: list, messages: dict) -> list:
        
        
        user_message = messages['content']
        context = self.rag_qdrant.search(user_message, self.rag_model,self.collection_name)
        
        interaction_final = PromptFormatter.format_prompt(interaction, textFormat(), context)
        print(interaction_final)
        return interaction_final

    @staticmethod
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

    def get_system_prompt(self):
        prompt = self.read_yaml_file()["system_prompt"]
        return [{"role": "system", "content": prompt}]

    # def conversation_handler(self, text: str, role: str, validator: bool):
    #     messages = {"role": role, "content": text}

    #     match role, validator:
    #         case "user", False:
    #             self.messages.append(messages)
    #             if len(self.validator_messages) > 6:
    #                 self.messages.pop(1)
    #                 self.messages.pop(2)
    #         case "user", True:
    #             self.validator_messages.append(messages)
    #             if len(self.validator_messages) > 2:
    #                 self.validator_messages.pop(1)
    #         case "assistant", False:
    #             self.messages.append(messages)
    #         case "assistant", True:
    #             self.validator_messages.append(messages)
    #         case _:
    #             raise ValueError("Invalid role")

    @staticmethod
    def __save_new_message_history(history_object: history, chat_id, interaction, history_data):
        history_object.save_new_message({'chat_id': chat_id,'interaction': interaction, 'history': history_data}, chat_id)
    
    def conversation_handler(self, text: str, role: str, chat_id: str, profile_name: str) -> list:
        messages = {"role": role, "content": text}
        interaction =  self.History.get_last_message(chat_id=chat_id)
        
        if interaction == 'Not finded':
            interaction = self.get_system_prompt()
            interaction = self.__rag(interaction, messages)
            interaction.append(messages)
            self.History.save_new_message({'profile_name': profile_name,'chat_id': chat_id,'interaction': interaction, 'history': interaction}, chat_id)
        
        else: 
            match role:
                case "user":
                    history = interaction['history']
                    interaction = interaction['interaction']
                    interaction[0] = self.get_system_prompt()[0]
                    #print(interaction)
                    interaction = self.__rag(interaction, messages)
                    interaction.append(messages)
                    
                    history.append(messages)
                    if len(interaction) > 8:
                        interaction.pop(1)
                        interaction.pop(2)
                    #self.History.save_new_message({'chat_id': chat_id,'interaction': interaction, 'history': history}, chat_id)
                    self.__save_new_message_history(self.History, chat_id, interaction,history)
                case "assistant": 
                    history = interaction['history']
                    interaction = interaction['interaction']
                    interaction.append(messages)
                    history.append(messages)
                    
                    # self.History.save_new_message({'chat_id': chat_id,'interaction': interaction, 'history': history}, chat_id)
                    self.__save_new_message_history(self.History, chat_id, interaction,history)
                case _:
                    raise ValueError('Invalid Role')
                
        return interaction
           
            
    def process(self, text: str, role: str, chat_id: str, profile_name: str):
        
        interaction = self.conversation_handler(text, role, chat_id, profile_name)

        start_time = time.time()
        completion = self.client.chat.completions.create(
            messages=interaction,
            model=self.model,
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=False,
        )

        chat_completion = completion.choices[0].message.content
        end_time = time.time()
        elapsed_time = int((end_time - start_time) * 1000)
        print(f"LLM ({elapsed_time}ms): {chat_completion}")
        self.conversation_handler(chat_completion, 'assistant', chat_id,profile_name)

        return chat_completion


class AsyncLLamager(LLamager):
    def __init__(self, option: str) -> None:
        super().__init__(option= option)
        self.client = AsyncGroq()

    async def conversation_handler(self, text: str, role: str, validator: bool):
        return super().conversation_handler(text, role, validator)

    async def process(self, text: str, role: str, validator: bool):
        await self.conversation_handler(text, role, validator)

        completion = await self.client.chat.completions.create(
            messages=self.validator_messages if validator else self.messages,
            model=self.validator_model if validator else self.model,
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=True,
        )

        return completion
