import os
from dotenv import find_dotenv, load_dotenv
import re
import pandas as pd
from azure.storage.blob import BlobServiceClient


load_dotenv(find_dotenv())
SAS_TOKEN = os.environ["SAS_TOKEN"]

storage_account_url = "https://pythonwhatsappbotstorage.blob.core.windows.net/"
container_name = "data"
blob_name = "04-2024_02.csv"
sas_token = SAS_TOKEN


def load_data_from_azure(storage_account_url, container_name, blob_name, sas_token):
    try:
        # Create a BlobServiceClient using the SAS Token and get a client to interact with the specified blob
        blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=sas_token)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        # Download the blob to a local memory stream
        with open("unit_price_temp.csv", "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        df = pd.read_csv("unit_price_temp.csv")

        return df

    except Exception as e:
        # Handle generic exceptions which could be related to Azure access issues, network problems, etc.
        print(f"Failed to load data from Azure Blob Storage: {e}")
        return None


def prepare_df():
    try:
        df = load_data_from_azure(storage_account_url, container_name, blob_name, sas_token)
        filtered_df = df[(df['Estado'] == 'CIUDAD DE MÉXICO') & (df['Ciudad'] == 'ÁLVARO OBREGÓN')]
        df2 = filtered_df[['Producto', 'Empaque', 'Marca', 'Precio_Unitario', 'Tienda']]
        return df2
    except Exception as e:
        print(f"Ocurrió un error al preparar el DataFrame: {e}")
        return None


def get_unit_price_of_product(producto, marca=None, empaque=None):
    df2 = prepare_df()
    if df2 is None:
        return "Falló la preparación del DataFrame."

    try:
        regex_producto = f".*{re.escape(producto[:-1])}.*"  # Manejo de plurales eliminando el último carácter
        df2 = df2[df2['Producto'].str.contains(regex_producto, case=False, na=False, regex=True)]

        if marca:
            regex_marca = f".*{re.escape(marca)}.*"
            df2 = df2[df2['Marca'].str.contains(regex_marca, case=False, na=False, regex=True)]

        if empaque:
            regex_empaque = f".*{re.escape(empaque)}.*"
            df2 = df2[df2['Empaque'].str.contains(regex_empaque, case=False, na=False, regex=True)]

        if df2.empty:
            return "No se encontraron productos que coincidan con los criterios."

        first_marca = df2['Marca'].iloc[0]
        first_empaque = df2['Empaque'].iloc[0]
        df2 = df2[(df2['Marca'] == first_marca) & (df2['Empaque'] == first_empaque)]

        if df2.empty:
            return "No se encontraron entradas coincidentes después de aplicar todos los filtros."

        # Calcular el precio promedio
        precio_promedio = round(df2['Precio_Unitario'].mean(), 2)

        # Eliminar duplicados y limitar a las primeras 5 tiendas únicas
        df2 = df2.drop_duplicates(subset='Tienda').head(5)

        result_string = f"Datos de PROFECO actualizados al 16 de abril de 2024\n{df2['Producto'].iloc[0]}, {first_marca}, {first_empaque}:\n"
        result_string += f"Precio promedio: ${precio_promedio:.2f}\n"
        for index, row in df2.iterrows():
            result_string += f"{row['Tienda']}: ${row['Precio_Unitario']}\n"

        return result_string

    except KeyError as e:
        return f"Error: El DataFrame no contiene la columna {e}"
    except re.error as e:
        return f"Error de expresión regular: {e}"
    except Exception as e:
        return f"Ocurrió un error inesperado: {e}"
    