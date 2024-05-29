from datetime import datetime, timedelta, timezone

def get_current_time():
    try:
        # Get the current UTC time using timezone-aware datetime
        now_utc = datetime.now(timezone.utc)
        # Adjust the time by subtracting 6 hours to convert to Mexico City time (Central Standard Time)
        now_local = now_utc - timedelta(hours=6)
        # Format the time in a readable format, for example: '11:00'
        time_str = now_local.strftime("%H:%M")
        return time_str
    except Exception as e:
        # Log or print an error message if an exception occurs
        return f"An error occurred: {e}"
