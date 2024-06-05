import pandas as pd
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
from datetime import timedelta
import os
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


def forecast_sales(product, n_days):
    try:
        # Load data
        df = load_data_from_azure(account_name, container_name, blob_name_load, sas_token)
        df.set_index('date', inplace=True)

        # Filter data by product using a case-insensitive regex match
        pattern = f".*{product}.*"  # Create a regex pattern that matches any part of the product name
        df = df[df['product'].str.contains(pattern, case=False, na=False)]

        # Check if data is available for the product
        if df.empty:
            return "No se encontró información acerca de ese producto."

        # Extract the actual product name from the first matched entry
        actual_product_name = df.iloc[0]['product']

        # Check for stationarity
        result = adfuller(df['sales'])

        # Make the series stationary if needed
        if result[1] > 0.05:
            df['sales_diff'] = df['sales'].diff().dropna()
            if df['sales_diff'].empty:
                return "No hay suficientes datos para realizar un pronóstico."
            data_for_model = df['sales_diff']
        else:
            data_for_model = df['sales']

        # Fit the ARIMA model
        model = ARIMA(data_for_model, order=(3, 1, 3))  # Modify the order based on your data analysis
        fitted_model = model.fit()

        # Forecast future sales
        forecast = round(fitted_model.forecast(steps=n_days), 0)
        return f"Las ventas pronosticadas para los siguientes {n_days} días de {actual_product_name} son: {forecast}"
    
    except FileNotFoundError:
        return "El archivo de datos no se encontró."
    except KeyError as e:
        return f"Columna faltante en los datos: {e}"
    except ValueError as e:
        return f"Error de valor: {e}"
    except Exception as e:
        return f"Ocurrió un error inesperado: {e}"


def forecast_sales2(product, n_days):
    try:
        # Load data
        df = pd.read_excel("Abarrotes Cruz.xlsx")
        df.set_index('date', inplace=True)

        # Filter data by product using a case-insensitive regex match
        pattern = f".*{product}.*"  # Create a regex pattern that matches any part of the product name
        df = df[df['product'].str.contains(pattern, case=False, na=False)]

        # Check if data is available for the product
        if df.empty:
            return "No se encontró información acerca de ese producto."

        # Check for stationarity
        result = adfuller(df['sales'])

        # Make the series stationary if needed
        if result[1] > 0.05:
            df['sales_diff'] = df['sales'].diff().dropna()
            if df['sales_diff'].empty:
                return "No hay suficientes datos para realizar un pronóstico."
            data_for_model = df['sales_diff']
        else:
            data_for_model = df['sales']

        # Fit the ARIMA model
        model = ARIMA(data_for_model, order=(3, 1, 3))  # Modify the order based on your data analysis
        fitted_model = model.fit()

        # Forecast future sales
        forecast = round(fitted_model.forecast(steps=n_days), 0)
        #return f"Las ventas pronosticadas para los siguientes {n_days} días son: {forecast}"
        return forecast.round(0)
    
    except FileNotFoundError:
        return "El archivo de datos no se encontró."
    except KeyError as e:
        return f"Columna faltante en los datos: {e}"
    except ValueError as e:
        return f"Error de valor: {e}"
    except Exception as e:
        return f"Ocurrió un error inesperado: {e}"


def predict_inventory_depletion(product, threshold_inventory):
    try:
        df = pd.read_excel("Abarrotes Cruz.xlsx")
        df.set_index('date', inplace=True)

        pattern = f".*{product}.*"  # Regex pattern to match any substring of the product name
        product_data = df[df['product'].str.contains(pattern, case=False, na=False)]

        if product_data.empty:
            return "No se encontraron datos para el producto especificado."

        latest_data = product_data.iloc[-1]
        initial_date = product_data.index[-1]
        current_inventory = latest_data['inventory']
        
        # Capture the actual product name from the latest entry
        actual_product_name = latest_data['product']

        if current_inventory <= threshold_inventory:
            return f"El inventario actual de {actual_product_name} ({current_inventory} unidades) ya está por debajo del umbral de {threshold_inventory} unidades. Considere reabastecer el inventario."

        forecasted_sales = forecast_sales2(product, 30)
        
        days_to_depletion = 0
        for sales in forecasted_sales:
            current_inventory -= sales
            days_to_depletion += 1
            if current_inventory <= threshold_inventory:
                depletion_date = initial_date + timedelta(days=days_to_depletion)
                return f"Se espera que el inventario de {actual_product_name} alcance las {threshold_inventory} unidades para el {depletion_date.date()}. ¿Quieres agregar un recordatorio de compra?"

        return "El nivel de inventario no alcanza el umbral dentro del período de pronóstico."
    
    except FileNotFoundError:
        return "No se encontró el archivo Excel especificado."
    except KeyError as e:
        return f"Falta una columna en los datos: {e}"
    except IndexError:
        return "Datos insuficientes para realizar la operación."
    except Exception as e:
        return f"Se produjo un error inesperado: {e}"
