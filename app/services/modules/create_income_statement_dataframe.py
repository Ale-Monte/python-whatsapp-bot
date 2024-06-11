import pandas as pd
import numpy as np
import os
from dotenv import find_dotenv, load_dotenv
from azure.storage.blob import BlobServiceClient


load_dotenv(find_dotenv())
SAS_TOKEN = os.environ["SAS_TOKEN"]

account_name = "pythonwhatsappbotstorage"
container_name = "data"
blob_name_load = "df_sales.xlsx"
sas_token = SAS_TOKEN
file_path_upload = "income_statement_dataframe.xlsx"
blob_name_upload = "income_statement_dataframe.xlsx"


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

def create_income_statement(df):
    try:
        def load_and_process_data(df):
            try:
                data = df
            except FileNotFoundError:
                return None, "File not found. Please check the file path."
            except Exception as e:
                return None, f"Error reading the Excel file: {e}"

            try:
                data['Date'] = pd.to_datetime(data['Date'])
                data['Year'] = data['Date'].dt.year
                data['Month'] = data['Date'].dt.month.map({
                    1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
                    7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
                })
                data['Total_Sales'] = data['Sales_Quantity'] * data['unit_sales_price']
                data['Total_Cost'] = data['Sales_Quantity'] * data['unit_purchase_cost']
                data['Profit'] = data['Total_Sales'] - data['Total_Cost']
            except KeyError as e:
                return None, f"Missing expected column in data: {e}"
            except Exception as e:
                return None, f"Error processing data: {e}"

            return data, None

        def aggregate_monthly(data):
            try:
                aggregates = data.groupby(['Month']).agg({
                    'Total_Sales': 'sum',
                    'Total_Cost': 'sum',
                    'Profit': 'sum'
                }).rename(columns={
                    'Total_Sales': 'Ventas',
                    'Total_Cost': 'Costo',
                    'Profit': 'Utilidad'
                })
                aggregates['Margen de Utilidad (%)'] = (aggregates['Utilidad'] / aggregates['Ventas'])
                months_order = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
                aggregates = aggregates.reindex(months_order, fill_value=0)
            except Exception as e:
                return None, f"Error aggregating monthly data: {e}"

            return aggregates, None

        def format_income_statement(aggregate_data, year):
            try:
                aggregate_data.loc['Total_Año'] = aggregate_data.sum(numeric_only=True)
                aggregate_data.loc['Total_Año', 'Margen de Utilidad (%)'] = aggregate_data.loc['Total_Año', 'Utilidad'] / aggregate_data.loc['Total_Año', 'Ventas']
                formatted = aggregate_data.T
                formatted.columns = [f'{year}_{col}' for col in formatted.columns]
            except Exception as e:
                return None, f"Error formatting income statement: {e}"

            return formatted, None

        def calculate_growth(all_years_data):
            try:
                for i in range(1, len(all_years_data)):
                    current_year, current_statement = all_years_data[i]
                    prev_year, prev_statement = all_years_data[i - 1]
                    for month in ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic', 'Total_Año']:
                        prev_year_col = f'{prev_year}_{month}'
                        current_year_col = f'{current_year}_{month}'
                        if prev_year_col not in prev_statement.columns or current_year_col not in current_statement.columns:
                            continue

                        prev_year_sales = prev_statement.loc['Ventas', prev_year_col]
                        current_year_sales = current_statement.loc['Ventas', current_year_col]
                        sales_growth = (current_year_sales - prev_year_sales) / prev_year_sales if prev_year_sales != 0 else None
                        if sales_growth == -1:
                            sales_growth = None
                        current_statement.loc['Crecimiento de Ventas (%)', current_year_col] = sales_growth

                        prev_year_profit = prev_statement.loc['Utilidad', prev_year_col]
                        current_year_profit = current_statement.loc['Utilidad', current_year_col]
                        profit_growth = (current_year_profit - prev_year_profit) / prev_year_profit if prev_year_profit != 0 else None
                        if profit_growth == -1:
                            profit_growth = None
                        current_statement.loc['Crecimiento de Utilidad (%)', current_year_col] = profit_growth

            except Exception as e:
                return None, f"Error calculating growth: {e}"

            return all_years_data, None

        def generate_income_statements(data):
            try:
                years = sorted(data['Year'].unique())  # Sort years in ascending order
                all_years_data = []
                for year in years:
                    yearly_data = data[data['Year'] == year]
                    monthly_data, error = aggregate_monthly(yearly_data)
                    if error:
                        return None, error
                    income_statement, error = format_income_statement(monthly_data, year)
                    if error:
                        return None, error
                    all_years_data.append((year, income_statement))
                
                # Calculate Sales and Profit Growth
                all_years_data, error = calculate_growth(all_years_data)
                if error:
                    return None, error

            except Exception as e:
                return None, f"Error generating income statements: {e}"

            return all_years_data, None

        # Process the data
        data, error = load_and_process_data(df)
        if error:
            return error

        all_years_data, error = generate_income_statements(data)
        if error:
            return error

        try:
            # Combine all years' data into a single DataFrame
            combined_data = pd.concat([statement.T for year, statement in all_years_data])

            # Replace zeros with NaN for specific columns
            metrics = ['Ventas', 'Costo', 'Utilidad', 'Margen de Utilidad (%)']
            combined_data[metrics] = combined_data[metrics].replace(0, np.nan)

            # Format percentage columns
            percentage_columns = ['Margen de Utilidad (%)', 'Crecimiento de Ventas (%)', 'Crecimiento de Utilidad (%)']
            for col in percentage_columns:
                combined_data[col] = combined_data[col].apply(lambda x: f'{x:.2%}' if pd.notnull(x) else '')

            # Round other columns with no decimal places
            other_columns = ['Ventas', 'Costo', 'Utilidad']
            for col in other_columns:
                combined_data[col] = combined_data[col].apply(lambda x: f'{x:.0f}' if pd.notnull(x) else '')

            # Save to Excel transposing rows and columns
            with pd.ExcelWriter('income_statement_dataframe.xlsx', engine='openpyxl') as writer:
                combined_data.to_excel(writer, header=True, index=True)

        except Exception as e:
            return f"Error saving to Excel: {e}"

        return "Income statement created successfully and saved as 'income_statement_dataframe.xlsx'."

    except Exception as e:
        return f"An unexpected error occurred: {e}"


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


df_sales = load_data_from_azure(account_name, container_name, blob_name_load, sas_token)
create_income_statement(df_sales)
message = upload_to_azure_with_sas(file_path_upload, account_name, container_name, blob_name_upload, sas_token)
print(message)
