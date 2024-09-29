import requests
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

import mp3_name

song_name = mp3_name.get_file_name()
print(song_name)

def search_music_metadata(query):
    base_url = "https://musicbrainz.org/ws/2/recording/"
    params = {
        'query': query,
        'fmt': 'json',
        'limit': 5  # limit to 5 results for brevity
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        # Parse the results
        results = []
        for recording in data.get('recordings', []):
            title = recording.get('title')
            artists = [artist['name'] for artist in recording['artist-credit']]
            release_info = recording.get('releases', [{}])[0]
            album = release_info.get('title')
            year = release_info.get('date', '').split('-')[0]  # Extract the year
            genre = None  # Genre might not be directly available in recording search

            results.append({
                'title': title,
                'contributing_artists': artists,
                'album': album,
                'year': year,
                'genre': genre  # You may need another request to fetch genre data
            })
        return results
    else:
        print(f"Error: {response.status_code}")
        return None


# Example usage
query = song_name
metadata = search_music_metadata(query)
for result in metadata:
    print(result)
