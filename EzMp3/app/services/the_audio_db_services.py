import requests
import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
import mp3_name

song_name = mp3_name.get_file_name()

def search_audiodb(title):
    # Base URL for TheAudioDB API (search for track)
    api_key = "2"  # Make sure to use your actual API key here
    base_url = f"https://www.theaudiodb.com/api/v1/json/{api_key}/searchtrack.php"

    # Parameters for the search
    params = {
        's': title  # Search by track name
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an error for bad responses

        data = response.json()

        # Check if there are results
        if 'track' in data and data['track']:
            for track in data['track']:
                contributing_artist = track['strArtist']
                album_artist = track.get('strAlbumArtist', 'N/A')  # Use .get() for safe access
                album = track['strAlbum']
                year = track['intYearReleased']
                genre = track['strGenre']

                print(f"Title: {title}")
                print(f"Contributing Artist: {contributing_artist}")
                print(f"Album Artist: {album_artist}")
                print(f"Album: {album}")
                print(f"Year: {year}")
                print(f"Genre: {genre}")
                print("\n" + "-" * 40 + "\n")
        else:
            print("No results found.")

    except requests.RequestException as e:
        print(f"An error occurred: {e}")

search_audiodb(song_name)