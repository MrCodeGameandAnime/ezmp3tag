# Assuming you have a function to fetch tags from Last.fm
import requests


def fetch_lastfm_tags(track, artist):
    """Fetch tags from Last.fm."""
    api_key = 'YOUR_LASTFM_API_KEY'  # Replace with your Last.fm API key
    url = f"http://ws.audioscrobbler.com/2.0/?method=track.getinfo&track={track}&artist={artist}&api_key={api_key}&format=json"

    try:
        response = requests.get(url)
        response_data = response.json()
        if 'track' in response_data:
            tags = response_data['track'].get('toptags', {}).get('tag', [])
            return [tag['name'] for tag in tags]  # Return list of tag names
    except Exception as e:
        print(f"Last.fm error: {e}")
    return []
