import os
from dotenv import find_dotenv, load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth


load_dotenv(find_dotenv())
spotify_client_id = os.environ['SPOTIFY_CLIENT_ID']
spotify_client_secret = os.environ['SPOTIFY_CLIENT_SECRET']


def create_spotify_oauth():
    try:
        return SpotifyOAuth(
        client_id=spotify_client_id,
        client_secret=spotify_client_secret,
        redirect_uri='http://localhost:8888/callback',
        scope='user-read-private user-modify-playback-state user-read-playback-state',
        cache_path='app/services/modules/.spotify_cache'
    )
    except Exception as e:
        print(f"Couldn't authenticate spotify: {e}")


def get_spotify_client():
    sp_oauth = create_spotify_oauth()
    try:
        token_info = sp_oauth.get_cached_token()

        # If token is not valid or not found, re-authenticate the user
        if not token_info or not sp_oauth.validate_token(token_info):
            auth_url = sp_oauth.get_authorize_url()
            print(f"Please navigate here and authorize: {auth_url}")
            response = input("Paste the URL you were redirected to here: ")
            code = sp_oauth.parse_response_code(response)
            token_info = sp_oauth.get_access_token(code, as_dict=True)  # Explicitly set as_dict to True

        return spotipy.Spotify(auth=token_info['access_token'])

    except spotipy.exceptions.SpotifyException as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


spotify_client = get_spotify_client()


def get_available_devices(sp=spotify_client):
    return sp.devices().get('devices', [])


def play_spotify_selection(search_query, search_type=None, artist=None, user_market='MX', sp=spotify_client):
    try:
        # Build the search query
        if artist:
            search_query = f'artist:{artist} {search_query}'

        # Perform the search
        if search_type:
            results = sp.search(q=search_query, type=search_type, limit=1, market=user_market)
        else:
            search_types = 'track,album,artist,playlist'
            results = sp.search(q=search_query, type=search_types, limit=1, market=user_market)

        # Parse search results
        for type_ in ['track', 'album', 'artist', 'playlist']:
            items = results.get(f'{type_}s', {}).get('items', [])
            if items:
                item = items[0]
                spotify_uri = item['uri']
                item_name = item['name']
                item_artist = item.get('artists', [{}])[0].get('name', '') if type_ in ['track', 'album'] else ''

                # Check for active device
                current_playback = sp.current_playback()
                if not current_playback:
                    devices = get_available_devices(sp)
                    if devices:
                        device_id = devices[0].get('id')
                    else:
                        return "No available devices found."
                else:
                    device_id = None  # Use the currently active device

                # Start playback
                if type_ == 'track' or not search_type:
                    sp.start_playback(device_id=device_id, uris=[spotify_uri])
                else:
                    sp.start_playback(device_id=device_id, context_uri=spotify_uri)
                play_message = f"Ahora reproduciendo: '{item_name}'"
                if item_artist:
                    play_message += f" de {item_artist}"
                return play_message

        return "No results found for your query."

    except spotipy.exceptions.SpotifyException as e:
        return f"Spotify API error: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

  
def control_playback(action, sp=spotify_client):
    try:
        if action == "next":
            sp.next_track()
            return "Playing next track."

        elif action == "previous":
            sp.previous_track()
            return "Playing previous track."

        elif action == "pause":
            sp.pause_playback()
            return "Playback paused."

        elif action == "play":
            sp.start_playback()
            return "Playback started."

        else:
            return "Invalid action."

    except Exception as e:
        return f"Error: {str(e)}"


def control_volume(action, volume_change=20, sp=spotify_client):
    try:
        current_playback = sp.current_playback()
        if not current_playback:
            return "No active playback found."

        current_volume = current_playback['device']['volume_percent']
        
        if action == "set":
            if 0 <= volume_change <= 100:  # Volume level must be between 0 and 100
                sp.volume(volume_change)
                return f"Volume set to {volume_change}%."
            else:
                return "Volume level must be between 0 and 100."

        elif action == "increase":
            new_volume = min(current_volume + volume_change, 100)  # Ensures volume does not exceed 100%
            sp.volume(new_volume)
            return f"Volume increased to {new_volume}%."

        elif action == "decrease":
            new_volume = max(current_volume - volume_change, 0)  # Ensures volume does not go below 0%
            sp.volume(new_volume)
            return f"Volume decreased to {new_volume}%."

        else:
            return "Invalid volume action."

    except Exception as e:
        return f"Error adjusting volume: {str(e)}"
    