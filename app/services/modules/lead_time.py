import shelve

def save_lead_time(product_name, lead_time):
    try:
        # Validate inputs
        if not isinstance(product_name, str) or not product_name:
            return "Invalid product name. It must be a non-empty string."
        if not isinstance(lead_time, (int, float)) or lead_time < 0:
            return "Invalid lead time. It must be a non-negative number."
        
        # Open the shelf file
        with shelve.open("product_lead_times.db") as db:
            # Save the lead time for the given product name
            db[product_name] = lead_time
        
        return f"El tiempo de entrega para '{product_name}' se ha guardado como {lead_time} días."
    
    except Exception as e:
        return f"An error occurred: {e}"
