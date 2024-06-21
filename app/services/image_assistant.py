import os
import logging
import shelve
from openai import OpenAI
from dotenv import find_dotenv, load_dotenv
import time

# Load environment variables and initialize the OpenAI client with the API key
load_dotenv(find_dotenv())
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def upload_image_to_openai(image_path):
    try:
        file = client.files.create(
            file=open(image_path, "rb"),
            purpose="vision"
        )
        return file.id
    except Exception as e:
        logging.error(f"Error uploading the image to OpenAI: {e}")
        return None


def create_new_assistant(image_id):
    try:
        # Create a new assistant each time
        assistant = client.beta.assistants.create(
            name="Creador de tickets de compra",
            model="gpt-4o",
            instructions=f"Eres un creador de tickets de compra. Extrae los nombres y cantidades de los productos de la imagen subida.Todos los tickets siempre siguen este formato: TICKET DE COMPRA #{image_id}:\n'Nombre de Producto 1': 'Cantidad de Producto 1'\n'Nombre de Producto 2': 'Cantidad de Producto 2'\n'Nombre de Producto 3': 'Cantidad de Producto 3'\n¿Quieres confirmar este ticket?"
        )
        return assistant.id
    except Exception as e:
        logging.error(f"Error creating a new assistant: {e}")
        return None


def get_or_create_thread(wa_id):
    try:
        with shelve.open("threads_db", writeback=True) as threads_shelf:
            thread_id = threads_shelf.get(wa_id)
            if not thread_id:
                thread = client.beta.threads.create()
                threads_shelf[wa_id] = thread.id
                thread_id = thread.id
        return thread_id
    except Exception as e:
        logging.error(f"Error accessing or creating the thread: {e}")
        return None


def generate_image_response(image_path, wa_id, image_id):
    try:
        file_id = upload_image_to_openai(image_path)
        if not file_id:
            return "Error uploading the image"

        thread_id = get_or_create_thread(wa_id)
        assistant_id = create_new_assistant(image_id)

        # First, send the image as part of the user's message
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=[
                {"type": "text", "text": f"Crea un ticket de compra basado en la imagen que te proporciono. Sigue el formato que conoces. TICKET DE COMPRA #{image_id}. Pregunta si quiero confirmar el ticket"},
                {
                    "type": "image_file",
                    "image_file": {"file_id": file_id}
                },
            ],
        )
        
        # Execute the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )
        while run.status not in ['completed', 'requires_action']:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        # Retrieve and return the last message from the assistant
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        new_message = messages.data[0].content[0].text.value
        return new_message

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return f"An error occurred: {e}"
