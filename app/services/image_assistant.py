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


def create_new_assistant():
    try:
        # Create a new assistant each time
        assistant = client.beta.assistants.create(
            name="Asistente de Análisis de Imágenes",
            model="gpt-4o",
            instructions="Analiza imágenes y proporciona información sobre ellas. Eres breve y muy conciso. Menciona solo lo esencial de la imagen. Se amable."
        )
        return assistant.id
    except Exception as e:
        logging.error(f"Error creating a new assistant: {e}")
        return None


def get_or_create_thread(user_id):
    try:
        with shelve.open("threads_db", writeback=True) as threads_shelf:
            thread_id = threads_shelf.get(user_id)
            if not thread_id:
                thread = client.beta.threads.create()
                threads_shelf[user_id] = thread.id
                thread_id = thread.id
        return thread_id
    except Exception as e:
        logging.error(f"Error accessing or creating the thread: {e}")
        return None


def generate_image_response(image_path, user_id):
    try:
        file_id = upload_image_to_openai(image_path)
        if not file_id:
            return "Error uploading the image"

        thread_id = get_or_create_thread(user_id)
        assistant_id = create_new_assistant()

        # First, send the image as part of the user's message
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=[
                {"type": "text", "text": "¿Qué hay en esta imagen?"},
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
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        # Retrieve and return the last message from the assistant
        messages = client.beta.threads.messages.list(thread_id=thread_id)
        new_message = messages.data[0].content[0].text.value
        return new_message

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return f"An error occurred: {e}"
    