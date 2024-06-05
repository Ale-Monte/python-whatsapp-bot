from app.services.modules.google_calendar import list_events, search_events, add_event
from app.services.modules.spotify import play_spotify_selection, control_playback, control_volume
from app.services.modules.unit_price import get_unit_price_of_product
from app.services.modules.clock import get_current_time
from app.services.modules.recomendacion_grafos import recommend_products_for
from app.services.modules.get_financial_metric import get_financial_metric
from app.services.modules.send_income_statement import get_income_statement_link
from app.services.modules.predict_sales import forecast_sales, predict_inventory_depletion
from app.services.modules.inventory_management import calculate_inventory_metrics


google_calendar_functions = [
    {
        "type": "function",
        "function": {
            "name": "list_events",
            "description": "List events within a specified number of days from now.",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "description": "Number of days to look ahead for events."}
                },
                "required": ["days"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_events",
            "description": "Search for events containing a specific keyword within a given number of days.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string", "description": "Keyword to search for in event summaries or descriptions."},
                    "days": {"type": "integer", "description": "Number of days to search from now.", "default": 30}
                },
                "required": ["keyword"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_event",
            "description": "Add a new event to the Google Calendar. Use corresponding emojis like: 🗓️",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Title of the event."},
                    "date": {"type": "string", "description": "Date of the event (YYYY-MM-DD)."},
                    "start_time": {"type": "string", "description": "Start time of the event (HH:MM)."},
                    "end_time": {"type": "string", "description": "End time of the event (HH:MM)."},
                    "location": {"type": "string", "description": "Location of the event."},
                    "notification": {"type": "integer", "description": "Minutes before the event to send a notification."},
                    "description": {"type": "string", "description": "Description of the event."}
                },
                "required": ["title", "date"]
            }
        }
    }
]

unit_price_functions = [
    {
        "type": "function",
        "function": {
            "name": "get_unit_price_of_product",
            "description": "Retrieves unit prices of a specified product per store. Mention the prices come from PROFECO.",
            "parameters": {
                "type": "object",
                "properties": {
                    "producto": {"type": "string", "description": "Single word that describes the primary product category or product type, e.g. 'Refresco', 'Papas', 'Pañales', 'Leche', 'Rastrillos'."},
                    "marca": {"type": "string", "description": "The brand of the product, e.g. 'Coca Cola', 'Fanta', 'Sabritas', 'Huggies', 'Gillette'."},
                    "empaque": {"type": "string", "description": "Specifies the packaging type of the product, e.g. '600 ml', '1 l', '12 piezas', '150 gr', 'Paketaxo'"}
                },
                "required": ["producto"]
            }
        }
    }
]

recommendation_functions = [
    {
        "type": "function",
        "function": {
            "name": "recommend_products_for",
            "description": "Provides product recommendations by identifying products that are frequently purchased together with the queried product. Tell the user the strength of the connection of the products.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string","description": "The product name or category to search for its related products."},
                    "top_n": {"type": "integer", "description": "Optional. The number of top connected products to return based on their frequency of being bought together.", "default": 5}
                },
                "required": ["query"]
            }
        }
    }
]

get_financial_metric_functions = [
    {
        "type": "function",
        "function": {
            "name": "get_financial_metric",
            "description": "Retrieves a specific financial metric for a given year and optionally a month from the store's income statement.",
            "parameters": {
                "type": "object",
                "properties": {
                    "financial_metric": {"type": "string", "description": "The name of the financial metric to retrieve.", "enum": ["Ventas", "Costo", "Utilidad", "Margen de Utilidad (%)", "Crecimiento de Ventas (%)", "Crecimiento de Utilidad (%)"]},
                    "year": {"type": "integer", "description": "The year for which the financial metric is needed. (YYYY)"},
                    "month": {"type": "string", "description": "Optional. The specific month for which the financial metric is needed.", "enum": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"], "default": None}
                },
                "required": ["financial_metric", "year"]
            }
        }
    }
]

send_income_statement_functions = [
    {
        "type": "function",
        "function": {
            "name": "get_income_statement_link",
            "description": "Returns the Google Sheets file link of the store's income statement/balance general. Use this emoji: 📑"
        }
    }
]

predict_sales_functions = [
    {
        "type": "function",
        "function": {
            "name": "forecast_sales",
            "description": "Forecast sales for a specified product over a given number of days.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {"type": "string", "description": "Name of the product for which sales are to be forecasted."},
                    "n_days": {"type": "integer", "description": "Number of days into the future for which to forecast sales."}
                },
                "required": ["product", "n_days"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "predict_inventory_depletion",
            "description": "Predict when the inventory of a specified product will deplete to a specified threshold level. Ask the user if they want to add a purchase reminder",
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {"type": "string", "description": "Name of the product for which inventory depletion is to be predicted."},
                    "threshold_inventory": {"type": "integer", "description": "Inventory level threshold below which the user should consider replenishing the product."}
                },
                "required": ["product", "threshold_inventory"]
            }
        }
    }
]

inventory_management_functions = [
    {
        "type": "function",
        "function": {
            "name": "calculate_inventory_metrics",
            "description": "Calculate the Economic Order Quantity (EOQ) and reorder point (ROP) for a specified product to determine how much to buy and when to buy it. Tell the user you used EOQ and ROP.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string", "description": "Name of the product for which inventory metrics are to be calculated."}
                },
                "required": ["product_name"]
            }
        }
    }
]

spotify_functions = [
    {
        "type": "function",
        "function": {
            "name": "play_spotify_selection",
            "description": "Play a selection on Spotify based on user input.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_query": {"type": "string", "description": "The main search term."},
                    "search_type": {"type": "string", "description": "The type of content (album, track, or playlist).", "enum": ["album", "track", "playlist"], "default": None},
                    "artist": {"type": "string", "description": "The artist name.", "default": None},
                },
                "required": ["search_query"]
            }
        }
    }, {
        "type": "function",
        "function": {
            "name": "control_playback",
            "description": "Control playback actions like playing the next track, previous track, pausing, and resuming on Spotify.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "The playback action to perform (next, previous, pause, play).","enum": ["next", "previous", "pause", "play"]}
                },
                "required": ["action"]
            }
        }
    }, {
        "type": "function",
        "function": {
            "name": "control_volume",
            "description": "Control the volume on Spotify, including setting, increasing, or decreasing the volume.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "The volume action to perform (set, increase, decrease).", "enum": ["set", "increase", "decrease"]},
                    "volume_change": {"type": "integer", "description": "The volume level to set, or the amount to increase/decrease (from 0 to 100).", "default": None}
                },
                "required": ["action"]
            }
        }
    }
]

clock_functions = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Retrieves the current system time. Read in 12hr format"
        }
    }
]


google_calendar_functions_dict = {
    "list_events": list_events,
    "search_events": search_events,
    "add_event": add_event
}

unit_price_functions_dict = {
    "get_unit_price_of_product": get_unit_price_of_product
}

recommendation_functions_dict = {
    "recommend_products_for": recommend_products_for
}

get_financial_metric_functions_dict = {
    "get_financial_metric": get_financial_metric
}

send_income_statement_functions_dict = {
    "get_income_statement_link": get_income_statement_link
}

predict_sales_functions_dict = {
    "forecast_sales": forecast_sales,
    "predict_inventory_depletion": predict_inventory_depletion

}

inventory_management_functions_dict = {
    "calculate_inventory_metrics": calculate_inventory_metrics
}

spotify_functions_dict = {
    "play_spotify_selection": play_spotify_selection,
    "control_playback": control_playback,
    "control_volume": control_volume
}

clock_functions_dict = { 
    "get_current_time": get_current_time
}

assistant_functions = google_calendar_functions + unit_price_functions + recommendation_functions + get_financial_metric_functions + send_income_statement_functions + predict_sales_functions + inventory_management_functions + spotify_functions + clock_functions
available_functions_dict = google_calendar_functions_dict | unit_price_functions_dict |  recommendation_functions_dict | get_financial_metric_functions_dict | send_income_statement_functions_dict | predict_sales_functions_dict | inventory_management_functions_dict | spotify_functions_dict | clock_functions_dict