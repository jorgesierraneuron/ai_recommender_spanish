from app.services.interfaces.interfaces import Irag, IjinjaFormatter, IprompFormatterRag
from app.utils.chatbot_utils import create_embbedings, format_generic_text
from app.services.qdrant_manager import qdrant_manager
from jinja2 import Environment, Template
from app.config.config import embeding_config



class QdrantRag(Irag):

    def __init__(self, qdrant_manager: qdrant_manager) -> None:
        super().__init__()
        self.qdrant = qdrant_manager

    @staticmethod
    def create_embedding(text, model, openai_key):
        return create_embbedings(text, model, openai_key)
    
    
    def search(self, text, model, collection) -> list:
        
        vector = self.create_embedding(text,model,embeding_config.OPENAI_KEY.value)
        response = self.qdrant.search(vector, collection)

        i = 1
        context_list=[]
        for context in response:
            context_dict = {
                f"context_{i}": format_generic_text(context.payload['text']),
                f"context_{i}_fuente": context.payload['fuente'],
                f"context_{i}_pagina": context.payload['pagina'],
                f"context_{i}_autor": context.payload['autor'],                                    
            }
            i += 1
            context_list.append(context_dict)

        return context_list

    
    
    

class jinja2Formatter(IjinjaFormatter):

    __env = Environment()

    def promtp_format(self,template_str: str, context: dict):
        
        template = self.__env.from_string(template_str)
        formatted_text = template.render(context)
        return formatted_text 
    
class textFormat(IjinjaFormatter):

    @staticmethod
    def prompt_format(prompt: str, variables: dict):

        return prompt.format(**variables)
    

class PromptFormatter(IprompFormatterRag): 

    @staticmethod
    def format_prompt(history_messages: list, formatter: IjinjaFormatter, context: list) -> list:

        prompt = history_messages[0]["content"]
        variables =  {
            'context': ' '.join(map(str, context))
        }
        formated_prompt=formatter.prompt_format(prompt,variables)
        history_messages[0] = {"role":"system", "content": formated_prompt}

        return history_messages





        
        
        



        
