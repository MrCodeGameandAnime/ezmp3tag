import requests

import os
import pylast
from dotenv import load_dotenv

load_dotenv()

# API Credentials
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_API_SECRET = os.getenv("LASTFM_API_SECRET")
LASTFM_USERNAME = os.getenv("LASTFM_USERNAME")
LASTFM_PASSWORD = pylast.md5(os.getenv("LASTFM_PASSWORD"))


def initialize_lastfm_client():
    if not LASTFM_API_KEY or not LASTFM_API_SECRET or not LASTFM_USERNAME or not LASTFM_PASSWORD:
        raise ValueError("Missing Last.fm API credentials in environment variables.")

    return pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=LASTFM_API_SECRET,
                                username=LASTFM_USERNAME, password_hash=LASTFM_PASSWORD)


# Create a global Last.fm client instance
lastfm = initialize_lastfm_client()


def fetch_lastfm_tags(track, artist):
    """Fetch tags from Last.fm."""
    try:
        # Use the Last.fm client to get track information
        track_obj = lastfm.get_track(artist, track)
        tags = track_obj.get_top_tags(limit=5)  # Fetch top 5 tags
        return [tag.item.name for tag in tags]  # Return list of tag names
    except Exception as e:
        print(f"Last.fm error: {e}")
    return []
