'''
import os
from pathlib import Path
from os import scandir

def list_files(path):
    for filename in os.listdir(path):
        filepath = os.path.join(path, filename)
        if os.path.isfile(filepath):
            print(filename)

def files_and_dirs():
    for data in Path().rglob('*'):
        if data.is_file():
            print(data)

            
current_directory = os.getcwd()

list_files(current_directory)
print('break')
files_and_dirs()
'''

import os
import fnmatch
global file_name

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

def set_file_name(value):
    file_name = value

def get_file_name():
    return file_name

directory_to_search = r'''C:\Users\User\Documents\Dev\Python\EzMp3\EzMp3\.venv\build\music_dir'''
mp3_files = find_mp3_files(directory_to_search)
file_name = mp3_files[0].strip('.mp3')