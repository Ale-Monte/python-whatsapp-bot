import os
import base64
import pickle
import json
import datetime
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Define the scope of API access
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/calendar.events']


def google_calendar_auth():
    creds = None
    try:
        # Decode the credentials from an environment variable
        encoded_credentials = os.getenv('GOOGLE_CREDENTIALS')
        json_credentials = base64.b64decode(encoded_credentials).decode('utf-8')

        # Decode the token from an environment variable
        encoded_token = os.getenv('GOOGLE_TOKEN')
        if encoded_token:
            creds = pickle.loads(base64.b64decode(encoded_token))

        # Authenticate using the decoded credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                creds = InstalledAppFlow.from_client_config(json.loads(json_credentials), SCOPES).run_local_server(port=0)
            
            # After obtaining new credentials, update the token environment variable accordingly
            os.environ['GOOGLE_TOKEN'] = base64.b64encode(pickle.dumps(creds)).decode('utf-8')

    except Exception as e:
        return f"Authentication failed: {str(e)}. Please check your environment variables and credentials."

    return creds


creds = google_calendar_auth()


def list_events(days, creds=creds):
    try:
        service = build('calendar', 'v3', credentials=creds)
        
        # Calculate time range in RFC3339 UTC 'Zulu' format using timezone-aware datetimes
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        end_time = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=days)).isoformat()

        # Fetch events from Google Calendar API
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end_time,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
        
        # Extract and collect basic details from each event
        basic_info_list = [
            {
                'title': event.get('summary', 'No Title'),
                'start': event['start'].get('dateTime', event['start'].get('date')),
                'end': event['end'].get('dateTime', event['end'].get('date'))
            }
            for event in events
        ]

        return str(basic_info_list)

    except Exception as e:
        return f"Failed to list events: {str(e)}. Please try again."


def search_events(keyword, days=30, creds=creds):
    try:
        service = build('calendar', 'v3', credentials=creds)
        
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        end_time = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=days)).isoformat()

        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end_time,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        matching_events = [
            event for event in events
            if keyword.lower() in event.get('summary', '').lower() or keyword.lower() in event.get('description', '').lower()
        ]
        
        if not matching_events:
            return f"No events found with the keyword '{keyword}'."

        important_info = [
            {
                'title': event.get('summary', 'No Title'),
                'start': event['start'].get('dateTime', event['start'].get('date')),
                'end': event['end'].get('dateTime', event['end'].get('date'))
            } for event in matching_events
        ]

        return str(important_info)

    except Exception as e:
        return f"Failed to search events: {str(e)}. Please try again."


def add_event(title, date, start_time=None, end_time=None, location=None, notification=None, description=None, creds=creds):
    service = build('calendar', 'v3', credentials=creds)
    event_time_zone = 'America/Mexico_City'

    try:
        if start_time:
            # Parse start and end times for timed event
            start_datetime = datetime.datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            end_datetime = datetime.datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M") if end_time else start_datetime + datetime.timedelta(hours=1)
            start = {'dateTime': start_datetime.isoformat(), 'timeZone': event_time_zone}
            end = {'dateTime': end_datetime.isoformat(), 'timeZone': event_time_zone}
        else:
            # Set as all-day event
            start = {'date': date}
            end = {'date': date}

        # Create the event dictionary
        event = {
            'summary': title,
            'location': location,
            'description': description,
            'start': start,
            'end': end
        }

        # Add a notification reminder if specified
        if notification and start_time:
            event['reminders'] = {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': notification},
                    {'method': 'popup', 'minutes': notification},
                ],
            }
        # Attempt to insert the event into the calendar
        service.events().insert(calendarId='primary', body=event).execute()
        return "Event created successfully."

    except Exception as e:
        # Handle any errors that occur during the API call
        return f"Failed to create the event: {str(e)}. Please try again."