import os
from pathlib import Path
import mutagen
from mutagen.mp3 import MP3
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