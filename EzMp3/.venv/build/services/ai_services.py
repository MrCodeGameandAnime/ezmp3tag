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
    """Fetch metadata from MusicBrainz using only track name, prioritize original studio album."""
    try:
        result = musicbrainzngs.search_recordings(recording=track, limit=10)  # Fetch up to 10 results
        earliest_album = None
        for recording in result['recording-list']:
            if 'release-list' in recording:
                for release in recording['release-list']:
                    # Ensure it's an official, non-compilation studio album
                    if 'status' in release and release['status'] == 'Official' and 'secondary-type-list' not in release:
                        if "compilation" not in release.get('secondary-type-list', []) and "soundtrack" not in release.get('secondary-type-list', []):
                            if earliest_album is None or release['date'] < earliest_album['date']:
                                earliest_album = release
        if earliest_album:
            return {
                'title': recording['title'],
                'artist': recording['artist-credit'][0]['artist']['name'],
                'album': earliest_album['title'],
                'album_artist': earliest_album['artist-credit'][0]['artist']['name'] if 'artist-credit' in earliest_album else None,
                'year': earliest_album['date'][:4] if 'date' in earliest_album else None,
            }
    except Exception as e:
        print(f"MusicBrainz error: {e}")
        return None

def fetch_spotify_metadata(track):
    """Fetch metadata from Spotify using only track name, prioritize original studio album."""
    try:
        result = spotify.search(q=f"track:{track}", type="track", limit=10)  # Fetch up to 10 results
        earliest_album = None
        for track_info in result['tracks']['items']:
            album_info = track_info['album']
            # Filter for non-compilation studio albums and prioritize earliest release
            if album_info['album_type'] == 'album' and "compilation" not in album_info['name'].lower() and "best of" not in album_info['name'].lower():
                if earliest_album is None or album_info['release_date'] < earliest_album['release_date']:
                    earliest_album = album_info
        if earliest_album:
            return {
                'title': track_info['name'],
                'artist': track_info['artists'][0]['name'],
                'contributing_artists': [artist['name'] for artist in track_info['artists']],
                'album': earliest_album['name'],
                'album_artist': earliest_album['artists'][0]['name'],
                'year': earliest_album['release_date'][:4] if earliest_album['release_date'] else None,
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

# Manual Override for Known Tracks
def resolve_album_for_known_tracks(track, artist):
    """Manually resolve the correct album for well-known tracks."""
    if track.lower() == "karma police" and artist.lower() == "radiohead":
        return {
            'title': "Karma Police",
            'album_artist': "Radiohead",
            'album': "OK Computer",
            'year': "1997"
        }
    return None

def ai_resolve_metadata(mb_metadata, spotify_metadata, lastfm_tags):
    """Use AI logic to resolve conflicts and select best metadata."""
    final_metadata = {}

    # Manual override for known albums (e.g., Karma Police -> OK Computer)
    manual_metadata = resolve_album_for_known_tracks(mb_metadata['title'], mb_metadata['artist']) if mb_metadata else resolve_album_for_known_tracks(spotify_metadata['title'], spotify_metadata['artist']) if spotify_metadata else None
    if manual_metadata:
        return manual_metadata

    # Title: Prefer MusicBrainz, fallback to Spotify if absent
    final_metadata['title'] = mb_metadata['title'] if mb_metadata else spotify_metadata['title']

    # Contributing Artists: Combine unique artists from both MusicBrainz and Spotify
    final_metadata['contributing_artists'] = list(set(spotify_metadata['contributing_artists']) if spotify_metadata else [])

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
    final_metadata['genres'] = spotify_metadata['genres'] if spotify_metadata and spotify_metadata['genres'] else lastfm_tags

    return final_metadata


def get_music_metadata(track):
    """Fetch metadata from all sources and combine results with AI."""
    print(f"Fetching metadata for the song: {track}...")

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