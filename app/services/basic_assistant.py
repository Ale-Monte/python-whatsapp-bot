from openai import OpenAI
from dotenv import find_dotenv, load_dotenv
import os
import time
import logging

load_dotenv(find_dotenv())
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

def create_assistant():
    """
    Create an AI assistant with specific instructions and configuration,
    and return the assistant's ID.
    """
    assistant = client.beta.assistants.create(
        name="General Assistance",
        instructions="Provide helpful and knowledgeable responses, be friendly and professional.",
        model="gpt-4-1106-preview",
    )
    return assistant.id  # Return the newly created assistant's ID

def run_assistant(assistant_id, message_body):
    """
    Create a thread, add a message, and run the assistant to generate a response.
    """
    # Create a new thread
    thread = client.beta.threads.create()

    # Add user message to the thread
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message_body,
    )

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

    # Wait for completion
    while run.status != "completed":
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Retrieve the Messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    logging.info(f"Generated message: {new_message}")
    return new_message

def generate_response(message_body):
    """
    Generate a response to the given message body using a new assistant instance.
    """
    assistant_id = create_assistant()  # Create a new assistant for each interaction
    return run_assistant(assistant_id, message_body)
