def save_lead_time(product_name, lead_time):
    try:
        lead_time = lead_time

        return f"El tiempo de entrega para '{product_name}' se ha guardado como {lead_time} días."
    
    except Exception as e:
        return f"An error occurred: {e}"
    