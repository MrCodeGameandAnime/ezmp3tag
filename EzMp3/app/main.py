# app/main.py
import os
import json
from services.ai_services import get_music_metadata
from utils.mp3_name import extract_mp3_name
from utils.music_tag_editor import change_mp3_metadata

# Directory paths
MUSIC_DIR = 'music_dir/'
EXPORT_DIR = 'services/metadata_exports/'


def save_metadata(song_title, metadata):
    """Saves the metadata to a JSON file."""
    filename = f"{song_title.replace(' ', '_').lower()}_metadata.json"
    file_path = os.path.join(EXPORT_DIR, filename)

    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    with open(file_path, 'w') as file:
        json.dump(metadata, file, indent=4)

    print(f"Metadata for '{song_title}' saved to {file_path}")


# app/main.py

def main():
    """Process all MP3 files in the directory and fetch metadata."""
    # Use extract_mp3_name to get the first MP3 file name
    song_title = extract_mp3_name()  # Automatically uses MP3_PATH

    if not song_title:
        print("No MP3 file found to process.")
        return

    # Fetch resolved metadata using ai_services
    resolved_metadata = get_music_metadata(song_title)

    if resolved_metadata:
        song_path = os.path.join(MUSIC_DIR, f"{song_title}.mp3")  # Construct the path

        # Pass individual metadata fields to change_mp3_metadata
        change_mp3_metadata(
            song_path,
            resolved_metadata.get('title'),  # new_title
            resolved_metadata.get('contributing_artists'),  # new_contributing_artist
            resolved_metadata.get('album_artist'),  # new_album_artist
            resolved_metadata.get('album'),  # new_album
            resolved_metadata.get('year'),  # new_year
            ', '.join(resolved_metadata.get('genres', []))  # new_genre as a string
        )
        save_metadata(song_title, resolved_metadata)
    else:
        print(f"No metadata found for '{song_title}'")


if __name__ == "__main__":
    main()
