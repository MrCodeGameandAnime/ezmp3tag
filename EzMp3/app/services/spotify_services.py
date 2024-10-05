import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv


load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

def get_spotify_client():
    """Create a Spotify client with proper authentication."""
    if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
        print("Spotify credentials are missing!")
        return None

    # Authenticate using the Client Credentials Flow
    client_credentials_manager = SpotifyClientCredentials(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET
    )
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def fetch_spotify_metadata(track):
    """Fetch metadata from Spotify using only track name, prioritize original studio album."""
    try:
        sp = get_spotify_client()
        if not sp:
            return None

        result = sp.search(q=f"track:{track}", type="track", limit=10)  # Fetch up to 10 results
        earliest_album = None
        selected_track = None
        for track_info in result['tracks']['items']:
            album_info = track_info['album']
            # Filter for non-compilation studio albums and prioritize earliest release
            if album_info['album_type'] == 'album' and "compilation" not in album_info['name'].lower() and "best of" not in album_info['name'].lower():
                if earliest_album is None or album_info['release_date'] < earliest_album['release_date']:
                    earliest_album = album_info
                    selected_track = track_info

        if earliest_album and selected_track:
            # Fetch genres for the primary artist
            artist_info = sp.artist(selected_track['artists'][0]['id'])
            genres = artist_info['genres'] if artist_info and artist_info.get('genres') else []

            return {
                'title': selected_track['name'],
                'artist': selected_track['artists'][0]['name'],
                'contributing_artists': [artist['name'] for artist in selected_track['artists']],
                'album': earliest_album['name'],
                'album_artist': earliest_album['artists'][0]['name'],
                'year': earliest_album['release_date'][:4] if earliest_album['release_date'] else None,
                'popularity': selected_track['popularity'],
                'genres': genres
            }
    except Exception as e:
        print(f"Spotify error: {e}")
        return None
