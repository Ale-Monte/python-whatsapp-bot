import json
import os
import logging

JSON_FILE_PATH = 'lead_times.json'

def ensure_json_file_exists():
    """Ensure the JSON file exists and initialize it if it doesn't."""
    if not os.path.exists(JSON_FILE_PATH):
        with open(JSON_FILE_PATH, 'w') as file:
            json.dump({}, file)

def save_lead_time(product_name, lead_time):
    try:
        logging.info(f"Saving lead time for {product_name}: {lead_time} days")

        # Validate inputs
        if not isinstance(product_name, str) or not product_name:
            logging.error("Invalid product name. It must be a non-empty string.")
            return "Invalid product name. It must be a non-empty string."
        if not isinstance(lead_time, (int, float)) or lead_time < 0:
            logging.error("Invalid lead time. It must be a non-negative number.")
            return "Invalid lead time. It must be a non-negative number."

        # Ensure the JSON file exists
        ensure_json_file_exists()

        # Load existing data
        with open(JSON_FILE_PATH, 'r') as file:
            lead_times = json.load(file)

        # Update the lead time for the given product name
        lead_times[product_name] = lead_time

        # Save the updated data back to the JSON file
        with open(JSON_FILE_PATH, 'w') as file:
            json.dump(lead_times, file, indent=4)

        logging.info(f"Lead time for {product_name} saved successfully")
        return f"El tiempo de entrega para '{product_name}' se ha guardado como {lead_time} días."
    
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return f"An error occurred: {e}"
    

print(save_lead_time('coca 300', 21))