from app.services.modules.google_calendar import list_events, search_events, add_event
from app.services.modules.clock import get_current_time


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

clock_functions_dict = { 
    "get_current_time": get_current_time
}

assistant_functions = google_calendar_functions + clock_functions
available_functions_dict = google_calendar_functions_dict | clock_functions_dict