from openai import OpenAI
import re
import os 
import glob
from app.config.config import embeding_config

client = OpenAI(api_key=embeding_config.OPENAI_KEY.value)

def create_embbedings(text, model):
        """
        Create embeddings based on a text
        """
        embed_model = model
        response = client.embeddings.create(input=text,model=embed_model)
        return response.data[0].embedding



def format_generic_text(input_text):
    # Replace tab characters with spaces
    text = input_text.replace('\t', ' ')

    # Split the text into lines based on common patterns (e.g., ":" or capitalized words)
    lines = re.split(r'(?<=:)|(?=\b[A-Z][a-z]+\b)', text)
    
    formatted_lines = []
    for line in lines:
        line = line.strip()
        if ':' in line:
            # Add a new line before section headers
            formatted_lines.append(f"\n{line}\n")
        elif re.match(r'\b[A-Z][a-z]+\b', line):
            # Add bullet points for lists
            formatted_lines.append(f"- {line}")
        else:
            formatted_lines.append(line)

    # Join the lines back together with appropriate new lines
    formatted_text = ' '.join(formatted_lines)

    # Clean up multiple new lines
    formatted_text = re.sub(r'\n{2,}', '\n\n', formatted_text)

    return formatted_text.strip()

def files_paths(ruta_carpeta, extension="pdf"):
    """
    Imprime las rutas de todos los archivos en una carpeta especificada con una extensión dada.
    
    Parámetros:
    ruta_carpeta (str): Ruta de la carpeta donde se encuentran los archivos.
    extension (str): Extensión de los archivos a imprimir, por defecto se imprimirán todas las rutas de archivos.
    """
    archivos = glob.glob(os.path.join(ruta_carpeta, f"*.{extension}"))
    
    return archivos



        