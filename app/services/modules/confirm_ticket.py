import json
import os
import csv
from openai import OpenAI
from dotenv import find_dotenv, load_dotenv
from datetime import datetime
from azure.storage.blob import BlobServiceClient
from app.services.modules.products_info import products_info

load_dotenv(find_dotenv())
SAS_TOKEN = os.environ["SAS_TOKEN"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)

account_name = "pythonwhatsappbotstorage"
container_name = "data"
sas_token = SAS_TOKEN
blob_name_upload = "sales_tickets.csv"


def upload_to_azure_with_sas(file_path, account_name, container_name, blob_name, sas_token):
    try:
        # Create the BlobServiceClient object using the SAS token and the account URL
        account_url = f"https://{account_name}.blob.core.windows.net"
        blob_service_client = BlobServiceClient(account_url=account_url, credential=sas_token)

        # Create a blob client using the local file name as the name for the blob
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        print(f"Uploading to Azure Storage as blob:\n\t{blob_name}")

        # Upload the created file
        with open(file_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)

        return f"File {file_path} uploaded to Azure Blob Storage successfully as {blob_name}."
    except Exception as ex:
        return f"An error occurred: {ex}"


products_info = products_info

# Default values for unknown products
default_product_id = 'U001'
default_unit_price = 10


def convert_ticket_to_json(input_string):
    # System message to instruct the model to output JSON
    system_message = "You are a helpful assistant designed to output JSON of a sales ticket."

    # User message containing the input string and the desired output format
    user_message = f"""Convert the following ticket information into a JSON object with the structure provided below:

    Input:
    {input_string}

    Output structure:
    {{
      "transaction_id": "string",
      "products": [
        {{
          "product_name": "string",
          "quantity": int
        }}
      ]
    }}
    """

    try:
        # Create the chat completion request
        response = client.chat.completions.create(
            model="gpt-4o",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        
        # Extract the JSON response content
        json_response = response.choices[0].message.content
        return json_response
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": "An unexpected error occurred"}


def update_tickets_csv(input_string):
    try:
        # Parse the JSON input
        json_string = convert_ticket_to_json(input_string)
        data = json.loads(json_string)
        
        # Get the current date
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Calculate the total value of the ticket
        ticket_value = 0
        for product in data['products']:
            product_name = product['product_name']
            unit_price = products_info.get(product_name, {'unit_price': default_unit_price})['unit_price'] # Gets default unit price value if the product is not found
            ticket_value += unit_price * product['quantity']

        # Open the CSV file for writing (append mode)
        file_exists = os.path.isfile('sales_tickets.csv')
        with open('sales_tickets.csv', mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write the header if the file is empty
            if not file_exists:
                writer.writerow(['Transaction ID', 'Date', 'Product Name', 'Product ID', 'Unit Price', 'Quantity', 'Product Value', 'Ticket Value'])
            
            # Write the data
            transaction_id = data['transaction_id']
            for product in data['products']:
                product_name = product['product_name']
                product_id = products_info.get(product_name, {'product_id': default_product_id})['product_id']
                unit_price = products_info.get(product_name, {'unit_price': default_unit_price})['unit_price']
                quantity = product['quantity']
                product_value = unit_price * quantity
                writer.writerow([transaction_id, current_date, product_name, product_id, unit_price, quantity, product_value, ticket_value])
        
        upload_to_azure_with_sas(blob_name_upload, account_name, container_name, blob_name_upload, sas_token)
        
        return f"CSV de tickets actualizado con {json_string} en {current_date}"
    except Exception as e:
        return f"An error occurred: {e}"
