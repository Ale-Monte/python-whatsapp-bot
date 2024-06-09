import logging
from flask import current_app, jsonify
import json
import requests
import re
from app.services.basic_assistant import generate_response
from app.services.image_assistant import generate_image_response


def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )


def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        return response

    
def get_media_url(media_id):
    url = f"https://graph.facebook.com/v20.0/{media_id}/"
    headers = {
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        media_data = response.json()
        return media_data.get('url')
    else:
        logging.error(f"Failed to retrieve media URL: {response.text}")
        return None


def download_image(image_url, image_id):
    path_to_save = f"{image_id}.jpg"  # Temporary file path

    headers = {
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}"
    }

    # Download the image with the appropriate headers
    response = requests.get(image_url, headers=headers, stream=True)
    if response.status_code == 200:
        with open(path_to_save, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return path_to_save
    else:
        logging.error(f"Failed to download the image: {response.text}")
        return None


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def process_whatsapp_message(body):
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    message_body = message["text"]["body"]

    # OpenAI Integration
    response = generate_response(message_body, wa_id)
    response = process_text_for_whatsapp(response)

    data = get_text_message_input(current_app.config["RECIPIENT_WAID"], response)
    send_message(data)


def process_image_message(body):
    message = body["entry"][0]["changes"][0]["value"]["messages"][0]
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    image_info = message.get("image", {})
    image_id = image_info.get('id')

    if image_id:
        image_url = get_media_url(image_id)  # Assume get_media_url returns the URL and MIME type
        if image_url:
            image_path = download_image(image_url, image_id)
            if image_path:
                response_text = generate_image_response(image_path, wa_id, image_id)
                response_text = process_text_for_whatsapp(response_text)

                # Preparing and sending the message back to WhatsApp
                data = get_text_message_input(current_app.config["RECIPIENT_WAID"], response_text)
                send_message(data)
            else:
                logging.error("Failed to download image.")
        else:
            logging.error("Image URL could not be retrieved.")
    else:
        logging.error("Image ID not found in the message.")


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )
