from app.services.modules.google_calendar import list_events, search_events, add_event
from app.services.modules.spotify import play_spotify_selection, control_playback, control_volume, add_song_to_queue
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
    }, {
        "type": "function",
        "function": {
            "name": "add_song_to_queue",
            "description": "Search for a track on Spotify and add it to the playback queue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_query": {"type": "string", "description": "The search query for the track to add to the queue."}
                },
                "required": ["search_query"]
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

spotify_functions_dict = {
    "play_spotify_selection": play_spotify_selection,
    "control_playback": control_playback,
    "control_volume": control_volume,
    "add_song_to_queue": add_song_to_queue,
}

clock_functions_dict = { 
    "get_current_time": get_current_time
}

assistant_functions = google_calendar_functions + spotify_functions + clock_functions
available_functions_dict = google_calendar_functions_dict | spotify_functions_dict | clock_functions_dict