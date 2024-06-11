import shelve

def save_lead_time(product_name, lead_time):
    try:
        with shelve.open('lead_time_shelf') as db:
            db[product_name] = lead_time
        return "¡Se registró exitosamente el tiempo de entrega! ¿Gustas volver a calcular la cantidad y el punto de reorden?"
    except Exception as e:
        return f"Ocurrió un error guardando el tiempo de entrega: {e}"
    