import pandas as pd
import os
from azure.storage.blob import BlobServiceClient
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())
SAS_TOKEN = os.environ["SAS_TOKEN"]

account_name = "pythonwhatsappbotstorage"
container_name = "data"
blob_name_load = "income_statement_dataframe.xlsx"
sas_token = SAS_TOKEN


def load_data_from_azure(account_name, container_name, blob_name, sas_token):
    try:
        # Create a BlobServiceClient using the SAS Token and get a client to interact with the specified blob
        blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net", credential=sas_token)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        # Define the local path to save the file
        local_file_path = f"./{blob_name}"
        
        # Download the blob to a local file
        with open(local_file_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        
        # Return the local file path instead of loading it into a DataFrame
        return local_file_path

    except Exception as e:
        # Handle generic exceptions which could be related to Azure access issues, network problems, etc.
        print(f"Failed to load data from Azure Blob Storage: {e}")
        return None


def get_financial_metric(financial_metric, year, month=None):
    try:
        file_path = load_data_from_azure(account_name, container_name, blob_name_load, sas_token)
        # Load the Excel file into a DataFrame
        df = pd.read_excel(file_path, index_col=0)
        
        # Determine the date string based on year and month
        if month is None:
            date = f"{year}_Total_Año"
        else:
            date = f"{year}_{month}"
        
        # Check if the date is in the index and the financial metric is in the columns
        if date in df.index and financial_metric in df.columns:
            value = df.loc[date, financial_metric]
            # Format the value
            if pd.notnull(value):
                if financial_metric in ['Margen (%)', 'Crecimiento de Ventas (%)', 'Crecimiento de Utilidad (%)']:
                    if isinstance(value, str) and value.endswith('%'):
                        value = float(value.strip('%')) / 100
                    formatted_value = f"{value:.2%}"
                else:
                    formatted_value = f"{int(value):,}"
                
                # Return the appropriate formatted string
                if month is None:
                    return f"El valor anual de {financial_metric} en {year} es: {formatted_value}"
                else:
                    return f"El valor de {financial_metric} en {month} {year} es: {formatted_value}"
            else:
                return "No se encontraron datos para esa fecha o métrica."
        else:
            return "No se encontraron datos para esa fecha o métrica."
    except Exception as e:
        return f"Error al leer el archivo de Excel: {e}"
