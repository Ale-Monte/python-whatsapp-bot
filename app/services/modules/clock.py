from datetime import datetime

def get_current_time():
    # Get the current time
    now = datetime.now()
    # Format the time in a readable format, for example: '15:45:00'
    time_str = now.strftime("%H:%M")
    
    return time_str