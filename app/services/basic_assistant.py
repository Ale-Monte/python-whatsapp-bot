from openai import OpenAI
from dotenv import find_dotenv, load_dotenv
import os
import time
import logging
import shelve
import json
from datetime import datetime
from app.services.functions import available_functions_dict


load_dotenv(find_dotenv())
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)
assistant_id = os.environ['OPENAI_ASSISTANT_ID']
available_functions = available_functions_dict
current_date = datetime.now().strftime("%Y-%m-%d")

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
    return tool_outputs


def run_assistant(thread_id, assistant_id, message_body):
    # Add user message to the thread and run the assistant.
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
        while run.status not in ['completed', 'requires_action']:
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
        if run.status == 'requires_action':
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

    return run_assistant(thread_id, assistant_id, message_body)
