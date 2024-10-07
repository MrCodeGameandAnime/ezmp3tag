from EzMp3.app.services.spotify_services import fetch_spotify_metadata
from EzMp3.app.services.musicbrainz_services import fetch_musicbrainz_metadata
from EzMp3.app.services.lastfm_services import fetch_lastfm_tags
from EzMp3.app.services.deezer_services import fetch_deezer_metadata
from EzMp3.app.services.discog_services import get_discogs_metadata
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
from datetime import datetime
import os
import json
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
    final_metadata = {}

    title_candidates = [
        spotify_metadata.get('title'),
        deezer_metadata.get('title'),
        mb_metadata.get('title'),
        discogs_metadata[0].get('title') if discogs_metadata else None
    ]
    title = next((t for t in title_candidates if t), None)
    if title:
        title = title.split(' - ')[0]
        title = title.split('(')[0].strip()
    final_metadata['title'] = title

    artist_candidates = [
        spotify_metadata.get('artist'),
        deezer_metadata.get('album_artist'),
        mb_metadata.get('artist'),
        discogs_metadata[0].get('artist')[0] if discogs_metadata and discogs_metadata[0].get('artist') else None
    ]
    final_metadata['contributing_artists'] = next((a for a in artist_candidates if a), None)

    final_metadata['album_artist'] = final_metadata['contributing_artists']

    album_candidates = [
        spotify_metadata.get('album'),
        deezer_metadata.get('album'),
        mb_metadata.get('album'),
        discogs_metadata[0].get('title') if discogs_metadata else None
    ]
    album = next((a for a in album_candidates if a), None)
    if album:
        album = album.split('(')[0].strip()
    final_metadata['album'] = album

    year_candidates = [
        spotify_metadata.get('year'),
        deezer_metadata.get('year'),
        mb_metadata.get('year'),
        discogs_metadata[0].get('year') if discogs_metadata else None
    ]
    years = [int(y) for y in year_candidates if y and y.isdigit()]
    final_metadata['year'] = str(min(years)) if years else None

    final_metadata['genres'] = (
        spotify_metadata.get('genres') or
        deezer_metadata.get('genres') or
        lastfm_tags or
        []
    )

    return final_metadata


def export_raw_and_resolved_metadata_to_json(spotify_metadata, mb_metadata, deezer_metadata, discogs_metadata,
                                             lastfm_tags, resolved_metadata, track_name):
    """Export the raw metadata from all sources and the resolved metadata to a JSON file."""
    # Define the filename, using the track name and current timestamp to avoid overwriting
    filename = f"{track_name.replace(' ', '_').lower()}_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    # Path to save the file
    output_dir = "metadata_exports"
    os.makedirs(output_dir, exist_ok=True)  # Ensure directory exists

    # Organize the metadata into a dictionary
    metadata_export = {
        "spotify_metadata": spotify_metadata,
        "musicbrainz_metadata": mb_metadata,
        "deezer_metadata": deezer_metadata,
        "discogs_metadata": discogs_metadata,
        "lastfm_tags": lastfm_tags,
        "resolved_metadata": resolved_metadata  # The final metadata resolved by AI
    }

    # Write the metadata to a file
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w') as json_file:
        json.dump(metadata_export, json_file, indent=4)

    print(f"Raw and resolved metadata for '{track_name}' has been exported to {filepath}")


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
               (discogs_metadata[0]['artist'] if discogs_metadata and discogs_metadata[0].get('artist') else
                (mb_metadata['artist'] if mb_metadata else None))))

    lastfm_tags = fetch_lastfm_tags(track, artist)

    # Combine metadata using AI decision making
    resolved_metadata = ai_resolve_metadata(mb_metadata, spotify_metadata, deezer_metadata, discogs_metadata,
                                            lastfm_tags)

    # Export both raw and resolved metadata to a JSON file after completion
    export_raw_and_resolved_metadata_to_json(spotify_metadata, mb_metadata, deezer_metadata, discogs_metadata,
                                             lastfm_tags, resolved_metadata, track)

    return resolved_metadata


if __name__ == "__main__":
    track_name = "Bohemian Rhapsody"
    metadata = get_music_metadata(track_name)
    print("AI-Resolved Metadata:", metadata)
