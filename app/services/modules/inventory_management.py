import pandas as pd
import numpy as np
import os
import shelve
from azure.storage.blob import BlobServiceClient
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())
SAS_TOKEN = os.environ["SAS_TOKEN"]

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

def set_lead_time(product_name, lead_time):
    try:
        with shelve.open('lead_time_shelf') as db:
            db[product_name] = lead_time
        return "¡Se registró exitosamente el tiempo de entrega! ¿Gustas volver a calcular la cantidad y el punto de reorden?"
    except Exception as e:
        return f"Ocurrió un error guardando el tiempo de entrega: {e}"


def calculate_inventory_metrics(product_name):
    try:
        # Load the data frame from Excel
        df = load_data_from_azure(account_name, container_name, blob_name_load, sas_token)
        
        # Filter the DataFrame for a specific product using regex for flexible matching
        pattern = f".*{product_name}.*"  # Create a regex pattern that matches any part of the product name
        df = df[df['product'].str.contains(pattern, case=False, na=False)]

        # Check if there are any data entries for the product
        if df.empty:
            return f"No hay información acerca del producto: {product_name}"

        # Extract the actual product name from the first matched entry
        actual_product_name = df.iloc[0]['product']

        lead_time = get_lead_time(actual_product_name)
        if lead_time is None:
            return f"No se encontró tiempo de entrega para {actual_product_name} (El tiempo de entrega es el tiempo que tarda en llegar el producto desde que se ordena). Por favor, ingrese el tiempo de entrega en días de {actual_product_name}:"

        # Constants
        interest_rate = 0.115

        # Exclude zero values and calculate mean cost per unit
        non_zero_costs = df['cost'][df['cost'] > 0]
        cost_per_unit = non_zero_costs.mean() if not non_zero_costs.empty else 0
        
        # Exclude zero values and calculate mean purchase quantity
        non_zero_purchases = df['purchases'][df['purchases'] > 0]
        purchase_quantity = non_zero_purchases.mean() if not non_zero_purchases.empty else 0
        
        ordering_cost = cost_per_unit * purchase_quantity * 0.48

        # Calculate Average Daily Demand
        sales_average = df['sales'].mean()
        
        # Calculate Standard Deviation of Sales for Safety Stock
        std_dev_demand = df['sales'].std()
        
        # Service level for Z-score, e.g., 95% confidence
        service_level = 1.2  # Approx. Z-score for 95% confidence
        
        # Calculate Safety Stock
        safety_stock = 5
        
        # Calculate Holding Cost 
        holding_cost_per_unit = cost_per_unit * interest_rate
        
        # Calculate EOQ
        eoq = round(np.sqrt((2 * sales_average * ordering_cost) / holding_cost_per_unit) if holding_cost_per_unit > 0 else 15, 0)
        
        # Calculate Reorder Point
        rop = round((sales_average * lead_time) + safety_stock, 0)
        
        return f"Cantidad a comprar (EOQ) para {actual_product_name}: {eoq} unidades, Nivel de reorden (ROP): {rop} unidades"
    except Exception as e:
        return f"An error occurred: {str(e)}"
