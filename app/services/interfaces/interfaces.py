from abc import ABC, abstractmethod


class IjinjaFormatter(ABC):

    @abstractmethod
    def prompt_format():
        pass 

    

class Irag(ABC):

    @abstractmethod
    def search():
        pass 

    @abstractmethod
    def create_embedding(): 
        pass 


class IprompFormatterRag(ABC):

    @abstractmethod
    def format_prompt(): 
        pass 


    