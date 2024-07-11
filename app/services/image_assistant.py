import os
import logging
import shelve
import time
import base64
import json
import requests
from openai import OpenAI
from dotenv import find_dotenv, load_dotenv
from app.services.modules.vectors import get_product_name
from app.services.modules.products_dictionary import products_dictionary
from datetime import datetime

# Load environment variables and initialize the OpenAI client with the API key
load_dotenv(find_dotenv())
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to encode the image
def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logging.error(f"Error encoding image: {e}")
        return None

def create_sales_ticket(image_path, image_id):
    base64_image = encode_image(image_path)
    if not base64_image:
        return "Error encoding image."

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    payload = {
        "model": "gpt-4o",
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": (
                    f'Eres responsable de extraer los nombres completos de los productos y sus cantidades. '
                    f'Extrae los nombres completos de cada producto y su cantidad. El nombre completo incluye: '
                    f'Tipo de producto, Marca, Descripción/Variedad, Tamaño/Peso.\n\nUsa este formato: '
                    f'{{"id_transaccion": {image_id}, "productos": [{{"nombre_producto": "nombre de producto 1", "cantidad": int}}, '
                    f'{{"nombre_producto": "nombre de producto 2", "cantidad": int}}]}}\n\nEjemplo de respuesta: '
                    f'{{"id_transaccion": {image_id}, "productos": [{{"nombre_producto": "Refresco, Coca-Cola, Regular, 1l", "cantidad": 2}}, '
                    f'{{"nombre_producto": "Galletas, Oreo, Chocolate, 200g", "cantidad": 3}}, {{'
                    f'"nombre_producto": "Cerveza, Victoria, Oscura, 600ml", "cantidad": 1}}]}}'
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Extrae los nombres completos de los productos y la cantidad de cada producto de la imagen que te proporciono. Sigue el formato que conoces. Asegúrate que siga un formato JSON."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        response_json = response.json()
        content = response_json['choices'][0]['message']['content']
        return content
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        return "Error processing request."

def format_ticket(json_response):
    try:
        data = json.loads(json_response)
        products = data['productos']

        total_cost = 0
        processed_products = []

        for product in products:
            product_string = product['nombre_producto']
            amount = product['cantidad']
            actual_product_name = get_product_name(product_string)
            product_cost = products_dictionary.get(actual_product_name, 0)
            total_product_cost = product_cost * amount
            total_cost += total_product_cost
            processed_products.append({
                'product_name': product_string.replace(',', ''),
                'amount': amount,
                'product_cost': product_cost,
                'total_product_cost': total_product_cost
            })

        output = []
        header = f"*FOLIO* #{data['id_transaccion']}"
        output.extend([
            "=" * 20,
            header,
            f"*FECHA*: {datetime.now().strftime('%d/%m/%Y')}",
            "=" * 20,
            ""
        ])

        for product in processed_products:
            output.extend([
                f"*PRODUCTO:* {product['product_name']}",
                f"*CANTIDAD:* {product['amount']}",
                f"*PRECIO:* ${product['product_cost']:.2f}",
                f"*IMPORTE:* ${product['total_product_cost']:.2f}",
                "-------------------------"
            ])

        output.extend([
            f"*TOTAL*: ${total_cost:.2f}",
            "",
            "¿Quieres confirmar este ticket?"
        ])

        return "\n".join(output)
    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding error: {e}")
        return "Error processing ticket."

def create_new_assistant():
    try:
        assistant = client.beta.assistants.create(
            name="Echo Assistant",
            model="gpt-4o",
            instructions="You are an echo assistant. Return exactly the same text you receive as input."
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

def echo_text(input_text, wa_id):
    try:
        thread_id = get_or_create_thread(wa_id)
        assistant_id = create_new_assistant()
        if not assistant_id:
            return "Error creating assistant."

        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=[
                {"type": "text", "text": input_text}
            ],
        )

        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )
        while run.status not in ['completed', 'requires_action']:
            time.sleep(0.5)
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

        messages = client.beta.threads.messages.list(thread_id=thread_id)
        return messages
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return f"An error occurred: {e}"
    
def generate_image_response(image_path, wa_id, image_id):
    try:
        sales_ticket = create_sales_ticket(image_path, image_id)
        formatted_ticket = format_ticket(sales_ticket)
        
        return formatted_ticket
    except Exception as e:
        logging.error(f"An error occurred in generate_image_response: {e}")
        return f"An error occurred: {e}"
