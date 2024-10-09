import os
import pylast
import httpx
from dotenv import load_dotenv
from urllib3.util.retry import Retry

load_dotenv()

# API Credentials
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_API_SECRET = os.getenv("LASTFM_API_SECRET")
LASTFM_USERNAME = os.getenv("LASTFM_USERNAME")
LASTFM_PASSWORD = pylast.md5(os.getenv("LASTFM_PASSWORD"))


def initialize_lastfm_client():
    if not LASTFM_API_KEY or not LASTFM_API_SECRET or not LASTFM_USERNAME or not LASTFM_PASSWORD:
        raise ValueError("Missing Last.fm API credentials in environment variables.")

    # Retry logic at the application level using httpx
    def retry_client():
        retries = 3  # Retry up to 3 times
        for attempt in range(retries):
            try:
                client = httpx.Client(timeout=10.0, verify=False)  # Disable SSL verification for now
                return client
            except httpx.RequestError as e:
                if attempt < retries - 1:  # Retry until max retries reached
                    print(f"Retrying... (attempt {attempt + 1})")
                else:
                    raise e

    client = retry_client()  # Create an HTTPX client with retry logic

    return pylast.LastFMNetwork(
        api_key=LASTFM_API_KEY,
        api_secret=LASTFM_API_SECRET,
        username=LASTFM_USERNAME,
        password_hash=LASTFM_PASSWORD
    )


lastfm = initialize_lastfm_client()


def fetch_lastfm_tags(track, artist):
    """Fetch tags from Last.fm."""
    try:
        # Use the Last.fm client to get track information
        track_obj = lastfm.get_track(artist, track)
        tags = track_obj.get_top_tags(limit=5)  # Fetch top 5 tags
        return [tag.item.name for tag in tags]  # Return list of tag names
    except pylast.NetworkError as e:
        print(f"Network error: {e}")
    except pylast.WSError as e:
        print(f"Last.fm API error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return []
