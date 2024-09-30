from spotify_services import fetch_spotify_metadata
from musicbrainz_services import fetch_musicbrainz_metadata
from lastfm_services import fetch_lastfm_tags
from deezer_services import fetch_deezer_metadata
from discog_services import get_discogs_metadata
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
from datetime import datetime
import os
import requests
import musicbrainzngs


load_dotenv()


def best_match(source_value, candidate_values):
    """Return the best match from candidate values based on similarity to the source value."""
    if not source_value or not candidate_values:
        return None

    best_candidate = None
    highest_ratio = 0

    for candidate in candidate_values:
        if candidate:  # Ensure the candidate is not None or empty
            ratio = fuzz.ratio(source_value.lower(), candidate.lower())
            if ratio > highest_ratio:
                highest_ratio = ratio
                best_candidate = candidate

    return best_candidate if highest_ratio >= 80 else (
        candidate_values[0] if candidate_values else None)  # Fallback to the first candidate


def parse_year(year_string):
    """Parse the year from a string and return it, or None if invalid."""
    try:
        # Handle cases with a full date
        if len(year_string) == 10:  # Format YYYY-MM-DD
            year = datetime.strptime(year_string, '%Y-%m-%d').year
        elif len(year_string) == 7:  # Format YYYY-MM
            year = datetime.strptime(year_string, '%Y-%m').year
        elif len(year_string) == 4:  # Format YYYY
            year = int(year_string)
        else:
            return None  # Invalid format

        return year
    except ValueError:
        return None  # Return None if parsing fails


def ai_resolve_metadata(mb_metadata, spotify_metadata, deezer_metadata, discogs_metadata, lastfm_tags):
    """Use AI logic to resolve conflicts and select the best metadata."""
    final_metadata = {}

    # Title: Prefer Spotify, then Deezer, then Discogs, then MusicBrainz
    final_metadata['title'] = spotify_metadata.get('title') if spotify_metadata else (
        deezer_metadata.get('title') if deezer_metadata else (
            discogs_metadata.get('title') if discogs_metadata else (
                mb_metadata.get('title') if mb_metadata else None
            )
        )
    )

    # Contributing Artists: Combine unique artists from all sources
    final_metadata['contributing_artists'] = list(set(
        (spotify_metadata.get('contributing_artists') if isinstance(spotify_metadata.get('contributing_artists'), list) else []) +
         (deezer_metadata.get('contributing_artists') if isinstance(deezer_metadata.get('contributing_artists'), list) else []) +
         (discogs_metadata['artist'] if isinstance(discogs_metadata, dict) and 'artist' in discogs_metadata else discogs_metadata) +  # Handle if 'artist' is a list or single item
         (mb_metadata.get('contributing_artists') if isinstance(mb_metadata.get('contributing_artists'), list) else [])
        )
    )

    # If discogs_metadata['artist'] is a list, flatten it
    if isinstance(discogs_metadata, list):
        final_metadata['contributing_artists'].extend(discogs_metadata)

    # Album Artist: Resolve album artist with handling for None values
    album_artist_spotify = spotify_metadata.get('album_artist', '')
    album_artist_deezer = deezer_metadata.get('album_artist', '')
    album_artist_discogs = discogs_metadata.get('album_artist', '') if isinstance(discogs_metadata, dict) else ''
    album_artist_mb = mb_metadata.get('album_artist', '')

    final_metadata['album_artist'] = max(
        [album_artist_spotify, album_artist_deezer, album_artist_discogs, album_artist_mb],
        key=lambda x: (x is not None and x != '', len(x) if x is not None else 0)
    )

    # Album: Prefer Spotify, then Deezer, then Discogs, then MusicBrainz
    final_metadata['album'] = spotify_metadata.get('album') if spotify_metadata else (
        deezer_metadata.get('album') if deezer_metadata else (
            discogs_metadata.get('title') if discogs_metadata else (
                mb_metadata.get('album') if mb_metadata else None
            )
        )
    )

    # Year: Prefer Spotify, then Deezer, then Discogs, then MusicBrainz
    final_metadata['year'] = spotify_metadata.get('year') if spotify_metadata else (
        deezer_metadata.get('year') if deezer_metadata else (
            discogs_metadata.get('year') if discogs_metadata else (
                mb_metadata.get('year') if mb_metadata else None
            )
        )
    )

    # Genres: Prefer Spotify genres, fallback to Deezer genres, then Last.fm tags if missing
    final_metadata['genres'] = (spotify_metadata.get('genres') if spotify_metadata and spotify_metadata.get('genres') else
                                (deezer_metadata.get('genres') if deezer_metadata and deezer_metadata.get('genres') else
                                 (lastfm_tags if lastfm_tags else [])))

    return final_metadata


def get_music_metadata(track):
    """Fetch metadata from all sources and combine results with AI."""
    print(f"Fetching metadata for the song: {track}...")

    # Fetch metadata in the specified order
    try:
        spotify_metadata = fetch_spotify_metadata(track)
    except Exception as e:
        print(f"Error fetching Spotify metadata: {e}")
        spotify_metadata = None

    try:
        deezer_metadata = fetch_deezer_metadata(track)
    except Exception as e:
        print(f"Error fetching Deezer metadata: {e}")
        deezer_metadata = None

    try:
        discogs_metadata = get_discogs_metadata(track)
    except Exception as e:
        print(f"Error fetching Discogs metadata: {e}")
        discogs_metadata = None

    try:
        mb_metadata = fetch_musicbrainz_metadata(track)
    except Exception as e:
        print(f"Error fetching MusicBrainz metadata: {e}")
        mb_metadata = None

    # Get the artist from one of the results (if possible) to improve Last.fm search
    artist = (spotify_metadata['artist'] if spotify_metadata else
              (deezer_metadata['album_artist'] if deezer_metadata else
               (discogs_metadata['album_artist'] if discogs_metadata else
                (mb_metadata['artist'] if mb_metadata else None))))

    lastfm_tags = fetch_lastfm_tags(track, artist)

    # Combine metadata using AI decision making
    metadata = ai_resolve_metadata(mb_metadata, spotify_metadata, deezer_metadata, discogs_metadata, lastfm_tags)

    return metadata


if __name__ == "__main__":
    track_name = "Bohemian Rhapsody"
    metadata = get_music_metadata(track_name)
    print("AI-Resolved Metadata:", metadata)