from app.services.data_load_vd import books_load
from app.services.qdrant_manager import qdrant_manager
from app.config.config import embeding_config
from app.utils.chatbot_utils import files_paths


# #new_book = books_load('KB/fuentes/mundodesofia.pdf',200,50,'El mundo de Sofia','Jostein Gaarder')


# load = books_load('KB/fuentes/mundodesofia.pdf',300,50,'El mundo de Sofia', 'Jostein Gaarder', embeding_config.OPENAI_KEY)

# data = load.prepare_data('El mundo de Sofia')['data']

# load_data = load.load_data(100,data,'books')

# print(data[0])


#sofia_database.delete_collection('books')

def create_colection(QdrantManager: qdrant_manager, name: str, dimensions: int):

    QdrantManager.create_collection(name, dimensions)

    return True

def load_data(book_load: books_load, dataset_name: str, collection_name: str): 
    
    data = book_load.prepare_data(dataset_name)['data']

    load_data = book_load.load_data(100,data,collection_name)

    return load_data

def main():

   # Create database 
    sofia_database = qdrant_manager(embeding_config.QDRANT_URL.value,embeding_config.QDRANT_API_KEY.value)
    create_colection(sofia_database,'ai_recommender_knowledge',1536)

#    Load data 
    for file_path in files_paths('files'):
        try:
            print(f'Processing: {file_path}')
            load = books_load(file_path,300,50,f'{file_path}', 'Neuron Studios', embeding_config.OPENAI_KEY.value)    
            status = load_data(load,'neuron_studios_internal_resources','ai_recommender_knowledge')
            yield status
        except Exception as e:
            yield f"Error al cargar datos desde el archivo {file_path}: {str(e)}"
    



if __name__ == "__main__":
   for status in main():
        print(f"Estado de la carga: {status}")
    



