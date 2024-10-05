import os
import fnmatch
from dotenv import load_dotenv

load_dotenv()
MP3_PATH = os.getenv("MP3_DIR")

if not os.path.exists(MP3_PATH):
    print("Directory does not exist:", MP3_PATH)


def find_mp3_files(directory):
    """Searches the specified directory and subdirectories for MP3 files and returns a list of file paths."""
    mp3_files = []

    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        # Filter for MP3 files
        for file in fnmatch.filter(files, '*.mp3'):
            # Append the full file path to the mp3_files list
            mp3_files.append(os.path.join(root, file))

    return mp3_files


def extract_mp3_name(mp3_path=None):
    """Extracts the name of the first MP3 file found in the specified path or returns None if no MP3 files are found."""
    # Use the provided path or fall back to the environment variable
    directory_to_search = mp3_path if mp3_path else MP3_PATH
    mp3_files = find_mp3_files(directory_to_search)

    if not mp3_files:
        print("No MP3 files found in the specified directory.")
        return None

    # Get the full path of the first MP3 file
    full_mp3_path = mp3_files[0]

    # Extract the base name (file name with extension)
    base_name = os.path.basename(full_mp3_path)

    # Remove the file extension
    mp3_name = os.path.splitext(base_name)[0]

    return mp3_name


if __name__ == "__main__":
    mp3_name = extract_mp3_name()
    if mp3_name:
        print(mp3_name)
