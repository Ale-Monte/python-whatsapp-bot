from dotenv import find_dotenv, load_dotenv
import os
import requests
import shelve
import pandas as pd
import numpy as np
from azure.storage.blob import BlobServiceClient

load_dotenv(find_dotenv())
SAS_TOKEN = os.environ["SAS_TOKEN"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
RECIPIENT_WAID = os.environ["RECIPIENT_WAID"]
PHONE_NUMBER_ID = os.environ["PHONE_NUMBER_ID"]
VERSION = os.environ["VERSION"]


account_name = "pythonwhatsappbotstorage"
container_name = "data"
blob_name_load = "Abarrotes Cruz.xlsx"
sas_token = SAS_TOKEN


def load_data_from_azure(account_name, container_name, blob_name, sas_token):
    try:
        # Create a BlobServiceClient using the SAS Token and get a client to interact with the specified blob
        blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net", credential=sas_token)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        # Download the blob to a local memory stream
        with open(blob_name_load, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        df = pd.read_excel(blob_name_load)

        return df

    except Exception as e:
        # Handle generic exceptions which could be related to Azure access issues, network problems, etc.
        print(f"Failed to load data from Azure Blob Storage: {e}")
        return None
    

def get_lead_time(product_name):
    with shelve.open('lead_time_shelf') as db:
        if product_name in db:
            return db[product_name]
        else:
            return None


def send_whatsapp_message(custom_message):
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": RECIPIENT_WAID,
        "type": "text",
        "text": {"body": custom_message},
    }
    response = requests.post(url, headers=headers, json=data)
    return response


def check_all_products_rop():
    try:
        # Load the data frame from Excel or Azure
        df = load_data_from_azure(account_name, container_name, blob_name_load, sas_token)
        
        if df.empty:
            return "No hay información acerca de los productos."

        products = list(df['product'].unique())

        for product_name in products:
            product_df = df[df['product'] == product_name]

            if product_df.empty:
                continue

            lead_time = get_lead_time(product_name)
            if lead_time is None:
                lead_time = 2

            interest_rate = 0.115

            non_zero_costs = product_df['cost'][product_df['cost'] > 0]
            cost_per_unit = non_zero_costs.mean() if not non_zero_costs.empty else 0

            non_zero_purchases = product_df['purchases'][product_df['purchases'] > 0]
            purchase_quantity = non_zero_purchases.mean() if not non_zero_purchases.empty else 0

            ordering_cost = cost_per_unit * purchase_quantity * 0.48

            sales_average = product_df['sales'].mean()

            std_dev_demand = product_df['sales'].std()

            service_level = 1.2

            safety_stock = 5

            holding_cost_per_unit = cost_per_unit * interest_rate

            eoq = round(np.sqrt((2 * sales_average * ordering_cost) / holding_cost_per_unit) if holding_cost_per_unit > 0 else 15, 0)
            print(eoq)

            rop = round((sales_average * lead_time) + safety_stock, 0)
            print(rop)

            latest_data = product_df.iloc[-1]
            current_inventory = latest_data['inventory']

            if current_inventory < rop:
                message = f"El inventario actual de {product_name} está por debajo del umbral de ROP de {rop} unidades. Se sugiere que reordene {eoq} unidades."
                send_whatsapp_message(message)
                # return message
            else:
                pass
                # return "No hay necesidad de reordenar producto."

    except FileNotFoundError:
        return "No se encontró el archivo Excel especificado."
    except KeyError as e:
        return f"Falta una columna en los datos: {e}"
    except IndexError:
        return "Datos insuficientes para realizar la operación."
    except Exception as e:
        return f"Se produjo un error inesperado: {e}"
    

check_all_products_rop()