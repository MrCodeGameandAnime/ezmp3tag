from flask import Flask, request, render_template, send_from_directory
import os
import shutil
from app.services.ai_services import get_music_metadata
from app.utils.mp3_name import extract_mp3_name
from app.utils.music_tag_editor import change_mp3_metadata
from dotenv import load_dotenv
import json

load_dotenv()
MP3_PATH = os.getenv("MP3_DIRECTORY")
app = Flask(__name__)

MUSIC_DIR = fr'{MP3_PATH}'
EXPORT_DIR = 'app/services/metadata_exports/'

# Ensure directories exist
os.makedirs(MUSIC_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)


def clear_music_directory():
    """Deletes all files in the MUSIC_DIR."""
    for filename in os.listdir(MUSIC_DIR):
        file_path = os.path.join(MUSIC_DIR, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


def save_metadata(song_title, metadata):
    """Saves the metadata to a JSON file."""
    filename = f"{song_title.replace(' ', '_').lower()}_metadata.json"
    file_path = os.path.join(EXPORT_DIR, filename)

    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    with open(file_path, 'w') as file:
        json.dump(metadata, file, indent=4)

    print(f"Metadata for '{song_title}' saved to {file_path}")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Clear the music directory before handling the new file
        clear_music_directory()

        if 'file' not in request.files:
            return "No file part", 400

        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400

        # Save the file to the music directory
        file_path = os.path.join(MUSIC_DIR, file.filename)
        file.save(file_path)

        # Process the uploaded file
        song_title = extract_mp3_name()  # Automatically uses MP3_PATH
        if not song_title:
            return "No MP3 file found to process.", 400

        # Fetch resolved metadata using ai_services
        resolved_metadata = get_music_metadata(song_title)
        if resolved_metadata:
            # Pass individual metadata fields to change_mp3_metadata
            change_mp3_metadata(
                file_path,
                resolved_metadata.get('title'),
                resolved_metadata.get('contributing_artists'),
                resolved_metadata.get('album_artist'),
                resolved_metadata.get('album'),
                resolved_metadata.get('year'),
                ', '.join(resolved_metadata.get('genres', []))
            )
            save_metadata(song_title, resolved_metadata)

            # Provide a download link for the updated MP3 file
            return f"""
                <h1>Processed metadata for '{song_title}'.</h1>
                <a href="/download/{file.filename}">Download Updated MP3</a>
            """, 200
        else:
            return f"No metadata found for '{song_title}'", 404

    return render_template("index.html")


@app.route("/download/<filename>")
def download_file(filename):
    """Serve the updated MP3 file for download."""
    return send_from_directory(MUSIC_DIR, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)


'''pre upload and download'''
# import os
# import json
# from dotenv import load_dotenv
# from flask import Flask, Blueprint, render_template, request, redirect, url_for
# from .services.ai_services import get_music_metadata
# from .utils.mp3_name import extract_mp3_name
# from .utils.music_tag_editor import change_mp3_metadata
# load_dotenv()
#
#
# MUSIC_DIR = os.getenv("MP3_DIRECTORY")
# EXPORT_DIR = 'services/metadata_exports/'
#
# # Flask app initialization
# app = Flask(__name__)
# bp = Blueprint('main', __name__)
#
#
# def save_metadata(song_title, metadata):
#     """Saves the metadata to a JSON file."""
#     filename = f"{song_title.replace(' ', '_').lower()}_metadata.json"
#     file_path = os.path.join(EXPORT_DIR, filename)
#
#     if not os.path.exists(EXPORT_DIR):
#         os.makedirs(EXPORT_DIR)
#
#     with open(file_path, 'w') as file:
#         json.dump(metadata, file, indent=4)
#
#     print(f"Metadata for '{song_title}' saved to {file_path}")
#
#
# @app.route("/", methods=["GET", "POST"])
# def index():
#     if request.method == "POST":
#         if 'file' not in request.files:
#             return "No file part", 400
#
#         file = request.files['file']
#         if file.filename == '':
#             return "No selected file", 400
#
#         # Save the file to the music directory
#         file_path = os.path.join(MUSIC_DIR, file.filename)
#         file.save(file_path)
#
#         # Process the uploaded file
#         song_title = extract_mp3_name()  # Automatically uses MP3_PATH
#         if not song_title:
#             return "No MP3 file found to process.", 400
#
#         # Fetch resolved metadata using ai_services
#         resolved_metadata = get_music_metadata(song_title)
#         if resolved_metadata:
#             # Pass individual metadata fields to change_mp3_metadata
#             change_mp3_metadata(
#                 file_path,
#                 resolved_metadata.get('title'),
#                 resolved_metadata.get('contributing_artists'),
#                 resolved_metadata.get('album_artist'),
#                 resolved_metadata.get('album'),
#                 resolved_metadata.get('year'),
#                 ', '.join(resolved_metadata.get('genres', []))
#             )
#             save_metadata(song_title, resolved_metadata)
#
#             # Provide a download link for the updated MP3 file
#             return f"""
#                 <h1>Processed metadata for '{song_title}'.</h1>
#                 <a href="/download/{file.filename}">Download Updated MP3</a>
#             """, 200
#         else:
#             return f"No metadata found for '{song_title}'", 404
#
#     return render_template("index.html")
#
#
# if __name__ == "__main__":
#     app.register_blueprint(bp)
#     app.run(debug=True)

'''pre flask'''
# import os
# import json
# from services.ai_services import get_music_metadata
# from utils.mp3_name import extract_mp3_name
# from utils.music_tag_editor import change_mp3_metadata
#
# # Directory paths
# MUSIC_DIR = 'music_dir/'
# EXPORT_DIR = 'services/metadata_exports/'
#
#
# def save_metadata(song_title, metadata):
#     """Saves the metadata to a JSON file."""
#     filename = f"{song_title.replace(' ', '_').lower()}_metadata.json"
#     file_path = os.path.join(EXPORT_DIR, filename)
#
#     if not os.path.exists(EXPORT_DIR):
#         os.makedirs(EXPORT_DIR)
#
#     with open(file_path, 'w') as file:
#         json.dump(metadata, file, indent=4)
#
#     print(f"Metadata for '{song_title}' saved to {file_path}")
#
#
# # app/main.py
#
# def main():
#     """Process all MP3 files in the directory and fetch metadata."""
#     # Use extract_mp3_name to get the first MP3 file name
#     song_title = extract_mp3_name()  # Automatically uses MP3_PATH
#
#     if not song_title:
#         print("No MP3 file found to process.")
#         return
#
#     # Fetch resolved metadata using ai_services
#     resolved_metadata = get_music_metadata(song_title)
#
#     if resolved_metadata:
#         song_path = os.path.join(MUSIC_DIR, f"{song_title}.mp3")  # Construct the path
#
#         # Pass individual metadata fields to change_mp3_metadata
#         change_mp3_metadata(
#             song_path,
#             resolved_metadata.get('title'),  # new_title
#             resolved_metadata.get('contributing_artists'),  # new_contributing_artist
#             resolved_metadata.get('album_artist'),  # new_album_artist
#             resolved_metadata.get('album'),  # new_album
#             resolved_metadata.get('year'),  # new_year
#             ', '.join(resolved_metadata.get('genres', []))  # new_genre as a string
#         )
#         save_metadata(song_title, resolved_metadata)
#     else:
#         print(f"No metadata found for '{song_title}'")
#
#
# if __name__ == "__main__":
#     main()
