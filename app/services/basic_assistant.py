from openai import OpenAI
from dotenv import find_dotenv, load_dotenv
import os
import time
import logging
import shelve

load_dotenv(find_dotenv())
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)
assistant_id = os.environ['OPENAI_ASSISTANT_ID']

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def check_if_thread_exists(wa_id):
    # Check if there is an existing thread ID for the given WhatsApp ID using shelve.
    try:
        with shelve.open("threads_db") as threads_shelf:
            return threads_shelf.get(wa_id, None)
    except Exception as e:
        logging.error(f"Error accessing threads database: {e}")
        return None

def store_thread(wa_id, thread_id):
    # Store a new thread ID for the given WhatsApp ID using shelve.
    try:
        with shelve.open("threads_db", writeback=True) as threads_shelf:
            threads_shelf[wa_id] = thread_id
    except Exception as e:
        logging.error(f"Error storing thread ID in database: {e}")


def run_assistant(thread_id, assistant_id, message_body):
    """Add user message to the thread and run the assistant."""
    try:
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message_body,
        )

        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )

        while run.status != "completed":
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        messages = client.beta.threads.messages.list(thread_id=thread_id)
        new_message = messages.data[0].content[0].text.value
        logging.info(f"Generated message: {new_message}")
        return new_message
    except Exception as e:
        logging.error(f"Error during assistant run: {e}")
        return "An error occurred while processing your request."


def generate_response(message_body, wa_id):
    # Generate a response using an existing or new thread based on WhatsApp ID.
    thread_id = check_if_thread_exists(wa_id)
    if thread_id is None:
        logging.info(f"Creating new thread for wa_id: {wa_id}")
        try:
            thread = client.beta.threads.create()
            store_thread(wa_id, thread.id)
            thread_id = thread.id
        except Exception as e:
            logging.error(f"Error creating new thread: {e}")
            return "Failed to initiate conversation."

    return run_assistant(thread_id, assistant_id, message_body)