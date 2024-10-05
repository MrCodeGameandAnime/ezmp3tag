import os
import fnmatch

def find_mp3_files(directory):
    """Searches the specified directory and subdirectories for mp3 files and returns a list of file paths."""
    mp3_files = []

    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        # Filter for mp3 files
        for file in fnmatch.filter(files, '*.mp3'):
            # Append the full file path to the mp3_files list
            mp3_files.append(os.path.join(file))

    return mp3_files


def get_first_mp3():
    directory_to_search = r'''C:\Users\User\Documents\Dev\Python\EzMp3\EzMp3\.venv\build\music_dir'''
    mp3_files = find_mp3_files(directory_to_search)
    return mp3_files[0].strip('.mp3')