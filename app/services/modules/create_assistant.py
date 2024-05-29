from openai import OpenAI
import os
from dotenv import load_dotenv
from app.services.functions import assistant_functions

# Load environment variables
load_dotenv()

# Retrieve API key from environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=OPENAI_API_KEY)

# Define the assistant's instructions and the tools it should use
instructions = "Eres un asistente especializado en ayudar tiendas pequeñas de abarrotes. Habla como una persona de manera amistosa y breve. Da tus respuestas de manera muy concisa y breve, explicando solo los puntos claves cómo en una conversación normal."

# Create the assistant
assistant = client.beta.assistants.create(
    name="Asistente Personal de Abarrotes",
    model="gpt-4o",
    instructions=instructions,
    tools=assistant_functions
)

# Print the assistant ID for further use
print("Assistant created with ID:", assistant.id)
