import os
import json
import time
import logging
import shelve
from datetime import datetime
from openai import OpenAI
from dotenv import find_dotenv, load_dotenv
from app.services.functions import assistant_functions, available_functions_dict


# Load environment variables, initialize the OpenAI client with API key, and retrieve the available functions dictionary.
load_dotenv(find_dotenv())
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)
available_functions = available_functions_dict

# Define configurations for the AI assistant, including the name, model, and instructions.
instructions = f"Eres un asistente especializado en ayudar tiendas pequeñas de abarrotes. Habla como una persona de manera amistosa y breve. Da tus respuestas de manera muy concisa y breve, explicando solo los puntos claves cómo en una conversación normal."
name="Asistente Personal de Abarrotes"
model="gpt-4o"

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def check_if_assistant_exists(current_date):
    # Check if there is an existing assistant ID for the given date using shelve.
    try:
        with shelve.open("assistants_db") as assistants_shelf:
            return assistants_shelf.get(current_date, None)
    except Exception as e:
        logging.error(f"Error accessing assistants database: {e}")
        return None

def store_assistant(current_date, assistant_id):
    # Store a new assistant ID for the given date using shelve.
    try:
        with shelve.open("assistants_db", writeback=True) as assistants_shelf:
            assistants_shelf[current_date] = assistant_id
    except Exception as e:
        logging.error(f"Error storing assistant ID in database: {e}")


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


def handle_tool_calls(tool_calls):
    tool_outputs = []
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_to_call = available_functions.get(function_name)

        if function_to_call and tool_call.function.arguments:
            logging.info(f"Arguments for {function_name}: {tool_call.function.arguments}")
            try:
                function_args = json.loads(tool_call.function.arguments)
                function_response = function_to_call(**function_args)
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": function_response
                })
            except json.JSONDecodeError:
                logging.error(f"Invalid JSON arguments for tool call {function_name}")
                continue
            except KeyError as e:
                logging.error(f"Missing function argument: {e}")
                continue
            except Exception as e:
                logging.error(f"Unexpected error during function call: {e}")
                continue
    return tool_outputs


def run_assistant(message_body, thread_id):
    # Update the current date each time the function runs
    current_date = datetime.now().strftime("%Y-%m-%d")
    # Dynamically change the instructions with today's date
    full_instructions = f"{instructions} La fecha de hoy es {current_date}."

    # Add user message to the thread and run the assistant.
    try:
        logging.info("Creating new assistant as none exists for today's date.")
        assistant_id = check_if_assistant_exists(current_date)
        if not assistant_id:
            assistant = client.beta.assistants.create(
                name=name,
                model=model,
                instructions=full_instructions,
                tools=assistant_functions
                )
            assistant_id = assistant.id
            store_assistant(current_date, assistant_id)
            logging.info(f"New assistant created and stored with ID {assistant_id} for date {current_date}.")

        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message_body,
        )
        logging.info("User message added to the thread.")
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )
        logging.info(f"Assistant run initiated for thread {thread_id}.")
        while run.status not in ['completed', 'requires_action']:
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            logging.info(f"Run status: {run.status}")
        if run.status == 'requires_action':
            logging.info("Handling required actions for the assistant run.")
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            tool_outputs = handle_tool_calls(tool_calls)
            client.beta.threads.runs.submit_tool_outputs(
                thread_id=thread_id,
                run_id=run.id,
                tool_outputs=tool_outputs
            )
        while run.status != 'completed':
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

    return run_assistant(message_body, thread_id)


print(generate_response('Hola como estas?', '1'))