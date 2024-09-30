import os
import requests
import musicbrainzngs
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pylast
from difflib import SequenceMatcher  # To compare the similarity of text for conflict resolution
from dotenv import load_dotenv
load_dotenv()


# API Credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
LASTFM_API_KEY = os.getenv("LASTFM_API_KEY")
LASTFM_API_SECRET = os.getenv("LASTFM_API_SECRET")
LASTFM_USERNAME = os.getenv("LASTFM_USERNAME")
LASTFM_PASSWORD = pylast.md5(os.getenv(("LASTFM_PASSWORD")))

# Initialize Spotify API client
spotify_auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET)
spotify = spotipy.Spotify(auth_manager=spotify_auth_manager)

# Initialize Last.fm API client
lastfm = pylast.LastFMNetwork(api_key=LASTFM_API_KEY, api_secret=LASTFM_API_SECRET, username=LASTFM_USERNAME,
                              password_hash=LASTFM_PASSWORD)

# Initialize MusicBrainz
musicbrainzngs.set_useragent("EzMP3Tags", "1.0", "https://EzMP3tags.com")


def fetch_musicbrainz_metadata(track):
    """Fetch metadata from MusicBrainz using only track name"""
    try:
        result = musicbrainzngs.search_recordings(recording=track, limit=1)
        recording = result['recording-list'][0]
        album = recording['release-list'][0] if 'release-list' in recording else None

        return {
            'title': recording['title'],
            'artist': recording['artist-credit'][0]['artist']['name'],
            'album': album['title'] if album else None,
            'album_artist': album['artist-credit'][0]['artist']['name'] if album else None,
            'year': album['date'][:4] if album and 'date' in album else None,
        }
    except Exception as e:
        print(f"MusicBrainz error: {e}")
        return None


def fetch_spotify_metadata(track):
    """Fetch metadata from Spotify using only track name"""
    try:
        result = spotify.search(q=f"track:{track}", type="track", limit=1)
        track_info = result['tracks']['items'][0]
        album_info = track_info['album']

        return {
            'title': track_info['name'],
            'artist': track_info['artists'][0]['name'],
            'contributing_artists': [artist['name'] for artist in track_info['artists']],
            'album': album_info['name'],
            'album_artist': album_info['artists'][0]['name'],
            'year': album_info['release_date'][:4] if album_info['release_date'] else None,
            'popularity': track_info['popularity'],
            'genres': spotify.artist(track_info['artists'][0]['id'])['genres']
        }
    except Exception as e:
        print(f"Spotify error: {e}")
        return None


def fetch_lastfm_tags(track, artist=None):
    """Fetch user-generated tags from Last.fm"""
    try:
        # If artist is known, use it, otherwise search by track alone
        if artist:
            track_obj = lastfm.get_track(artist, track)
        else:
            result = lastfm.search_for_track("", track)  # Search for track only
            track_obj = result.get_next_page()[0]  # Get the first search result

        tags = track_obj.get_top_tags(limit=5)
        return [tag.item.name for tag in tags]
    except Exception as e:
        print(f"Last.fm error: {e}")
        return None


def ai_resolve_metadata(mb_metadata, spotify_metadata, lastfm_tags):
    """Use AI logic to resolve conflicts and select best metadata"""
    final_metadata = {}

    # Title: Prefer MusicBrainz, fallback to Spotify if absent
    final_metadata['title'] = mb_metadata['title'] if mb_metadata else spotify_metadata['title']

    # Contributing Artists: Combine unique artists from both MusicBrainz and Spotify
    final_metadata['contributing_artists'] = list(
        set(spotify_metadata['contributing_artists']) if spotify_metadata else [])

    # Artist (Album Artist): Resolve album artist using string similarity
    album_artist_mb = mb_metadata['album_artist'] if mb_metadata else ''
    album_artist_spotify = spotify_metadata['album_artist'] if spotify_metadata else ''
    if album_artist_mb and album_artist_spotify:
        similarity = SequenceMatcher(None, album_artist_mb.lower(), album_artist_spotify.lower()).ratio()
        final_metadata['album_artist'] = album_artist_mb if similarity > 0.8 else album_artist_spotify
    else:
        final_metadata['album_artist'] = album_artist_mb or album_artist_spotify

    # Album: Prefer MusicBrainz, fallback to Spotify
    final_metadata['album'] = mb_metadata['album'] if mb_metadata else spotify_metadata['album']

    # Year: Prefer MusicBrainz, fallback to Spotify
    final_metadata['year'] = mb_metadata['year'] if mb_metadata else spotify_metadata['year']

    # Genres: Prefer Spotify genres, fallback to Last.fm tags if missing
    final_metadata['genres'] = spotify_metadata['genres'] if spotify_metadata and spotify_metadata[
        'genres'] else lastfm_tags

    return final_metadata


def get_music_metadata(track):
    """Fetch metadata from all sources and combine results with AI"""
    print(f"Fetching metadata for track: {track}...")

    # Fetch metadata from different APIs
    mb_metadata = fetch_musicbrainz_metadata(track)
    spotify_metadata = fetch_spotify_metadata(track)

    # Get the artist from one of the results (if possible) to improve Last.fm search
    artist = mb_metadata['artist'] if mb_metadata else (spotify_metadata['artist'] if spotify_metadata else None)
    lastfm_tags = fetch_lastfm_tags(track, artist)

    # Combine metadata using AI decision making
    metadata = ai_resolve_metadata(mb_metadata, spotify_metadata, lastfm_tags)

    return metadata


# Example usage
track_name = "Karma Police"

metadata = get_music_metadata(track_name)
print("AI-Resolved Metadata:", metadata)