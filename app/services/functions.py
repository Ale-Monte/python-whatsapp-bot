from app.services.modules.google_calendar import list_events, search_events, add_event
from app.services.modules.spotify import play_spotify_selection, control_playback, control_volume
from app.services.modules.unit_price import get_unit_price_of_product
from app.services.modules.clock import get_current_time
from app.services.modules.recomendacion_grafos import recommend_products_for


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
            "description": "Add a new event to the Google Calendar.",
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
            "description": "Retrieves unit prices of a specified product per store.",
            "parameters": {
                "type": "object",
                "properties": {
                    "producto": {"type": "string", "description": "Primary product category or product type, e.g. 'Refresco', 'Papas', 'Pañales', 'Leche', 'Rastrillos'."},
                    "marca": {"type": "string", "description": "The brand of the product, e.g. 'Coca Cola', 'Fanta', 'Sabritas', 'Huggies', 'Gillette'."},
                    "empaque": {"type": "string", "description": "Specifies the packaging type of the product, e.g. '600 ml', '1 l', '12 piezas', '150 gr'"}
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
            "description": "Provides product recommendations by identifying products that are frequently purchased together with the queried product.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string","description": "The product name or category to search for its related products."},
                    "top_n": {"type": "integer", "description": "The number of top connected products to return based on their frequency of being bought together.", "default": 5}
                },
                "required": ["query"]
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
            "description": "Retrieves the current system time. Read in 12hr format",
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

spotify_functions_dict = {
    "play_spotify_selection": play_spotify_selection,
    "control_playback": control_playback,
    "control_volume": control_volume
}

clock_functions_dict = { 
    "get_current_time": get_current_time
}

assistant_functions = google_calendar_functions + unit_price_functions + recommendation_functions + spotify_functions + clock_functions
available_functions_dict = google_calendar_functions_dict | unit_price_functions_dict |  recommendation_functions_dict | spotify_functions_dict | clock_functions_dict