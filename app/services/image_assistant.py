import requests
import logging
import os
from openai import OpenAI
from dotenv import find_dotenv, load_dotenv


load_dotenv(find_dotenv())
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
client = OpenAI(api_key=OPENAI_API_KEY)


def generate_image_response(base64_image, wa_id):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    # OpenAI payload with the base64 encoded image
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What's in this image?"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    # Sending request to OpenAI
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    if response.status_code == 200:
        response_data = response.json()
        try:
            # Extract the text response from OpenAI
            text_content = response_data['choices'][0]['message']['content']
            return text_content
        except (KeyError, IndexError, TypeError):
            logging.error("Failed to parse OpenAI response")
            return "Failed to analyze image."
    else:
        logging.error(f"OpenAI API error: {response.text}")
        return "Error in processing image analysis."
