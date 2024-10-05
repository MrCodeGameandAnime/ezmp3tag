from flask import Blueprint, request, jsonify, send_file
import os
from app.services.ai_services import get_music_metadata
from app.utils.mp3_name import extract_mp3_name
from app.utils.music_tag_editor import change_mp3_metadata
import json

'''
API Usage Overview
The API routes are accessible with the /api prefix:

File Upload: POST /api/upload
Download MP3: GET /api/download/<filename>
Welcome Message: GET /
Example URL Calls:

File Upload: http://127.0.0.1:5000/api/upload
File Download: http://127.0.0.1:5000/api/download/your_file.mp3
'''


api = Blueprint('api', __name__)

MUSIC_DIR = os.getenv("MP3_DIRECTORY", 'app/music_dir/')
EXPORT_DIR = 'app/services/metadata_exports/'

# Ensure directories exist
os.makedirs(MUSIC_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)


def save_metadata(song_title, metadata):
    """Saves the metadata to a JSON file."""
    filename = f"{song_title.replace(' ', '_').lower()}_metadata.json"
    file_path = os.path.join(EXPORT_DIR, filename)

    with open(file_path, 'w') as file:
        json.dump(metadata, file, indent=4)

    return file_path


def process_metadata(file_path, song_title):
    """Process the metadata and update MP3 file."""
    resolved_metadata = get_music_metadata(song_title)
    if resolved_metadata:
        change_mp3_metadata(
            file_path,
            resolved_metadata.get('title'),
            resolved_metadata.get('contributing_artists'),
            resolved_metadata.get('album_artist'),
            resolved_metadata.get('album'),
            resolved_metadata.get('year'),
            ', '.join(resolved_metadata.get('genres', []))
        )
        metadata_file_path = save_metadata(song_title, resolved_metadata)
        return True, metadata_file_path
    return False, None


@api.route("/", methods=["GET"])
def welcome():
    """Welcome message for the API."""
    return jsonify({"message": "Welcome to the Music Metadata API! Use /api/upload to upload music files."})


@api.route("/upload", methods=["POST"])
def upload_file():
    """API endpoint for Android app to upload MP3 file and analyze metadata."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the file to the music directory
    file_path = os.path.join(MUSIC_DIR, file.filename)
    file.save(file_path)

    # Extract MP3 name and process metadata
    song_title = extract_mp3_name(file_path)
    if not song_title:
        return jsonify({"error": "No MP3 file found to process."}), 400

    # Process the metadata
    success, metadata_file = process_metadata(file_path, song_title)
    if success:
        return jsonify({
            "message": f"Metadata processed for '{song_title}'.",
            "download_url": f"/api/download/{os.path.basename(file_path)}"  # Updated URL to include /api
        }), 200
    else:
        return jsonify({"error": f"No metadata found for '{song_title}'."}), 404


@api.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    """Serve the updated MP3 file for download."""
    file_path = os.path.join(MUSIC_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        return jsonify({"error": "File not found"}), 404
