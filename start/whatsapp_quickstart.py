from dotenv import find_dotenv, load_dotenv
import os
import requests

# --------------------------------------------------------------
# Load environment variables
# --------------------------------------------------------------

load_dotenv(find_dotenv())
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
RECIPIENT_WAID = os.environ["RECIPIENT_WAID"]
PHONE_NUMBER_ID = os.environ["PHONE_NUMBER_ID"]
VERSION = os.environ["VERSION"]

APP_ID = os.environ["APP_ID"]
APP_SECRET = os.environ["APP_SECRET"]

# --------------------------------------------------------------
# Send a template WhatsApp message
# --------------------------------------------------------------


def send_whatsapp_message():
    url = f"https://graph.facebook.com/{VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    data = {
        "messaging_product": "whatsapp",
        "to": RECIPIENT_WAID,
        "type": "template",
        "template": {"name": "hello_world", "language": {"code": "en_US"}},
    }
    response = requests.post(url, headers=headers, json=data)
    return response


# Call the function
response = send_whatsapp_message()
print(response.status_code)
print(response.json())
