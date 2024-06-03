import os
import base64
import pickle
import json
from dotenv import find_dotenv, load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from azure.storage.blob import BlobServiceClient

load_dotenv(find_dotenv())
SAS_TOKEN = os.environ["SAS_TOKEN"]

account_name = "pythonwhatsappbotstorage"
container_name = "data"
blob_name_load = "income_statement_visual.xlsx"
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
    

# Define the scope of API access
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']

def sheets_auth():
    creds = None
    try:
        # Decode the credentials from an environment variable
        encoded_credentials = os.getenv('SHEETS_CREDENTIALS')
        json_credentials = base64.b64decode(encoded_credentials).decode('utf-8')

        # Decode the token from a different environment variable
        encoded_token = os.getenv('SHEETS_TOKEN')
        if encoded_token:
            creds = pickle.loads(base64.b64decode(encoded_token))

        # Authenticate using the decoded credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(json.loads(json_credentials), SCOPES)
                creds = flow.run_local_server(port=8080)
            
            # After obtaining new credentials, update the token environment variable accordingly
            os.environ['SHEETS_TOKEN'] = base64.b64encode(pickle.dumps(creds)).decode('utf-8')

    except Exception as e:
        return f"Authentication failed: {str(e)}. Please check your environment variables and credentials."

    return creds

creds = sheets_auth()
# Build the Drive service
drive_service = build('drive', 'v3', credentials=creds)

def get_income_statement_link():
    file_metadata = {
        'name': 'Estado de Resultados',
        'mimeType': 'application/vnd.google-apps.spreadsheet'  # This tells Drive to convert the file to Google Sheets
    }

    try:
        file_path = load_data_from_azure(account_name, container_name, blob_name_load, sas_token)
        media = MediaFileUpload(file_path,
                                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                                resumable=True)

        # Requesting the webViewLink along with the id
        file = drive_service.files().create(body=file_metadata,
                                      media_body=media,
                                      fields='id, webViewLink').execute()

        return f"Puedes ver el estado de resultados en: {file.get('webViewLink')}"

    except FileNotFoundError:
        # Handle the case where the Excel file isn't found
        return "The file was not found. Please check the file path."

    except Exception as error:
        # Handle other possible exceptions
        return f"An unexpected error occurred: {str(error)}"

# Path to your Excel file

# Upload and convert the file, and retrieve the web view link
google_sheet_link = get_income_statement_link()
print(google_sheet_link)