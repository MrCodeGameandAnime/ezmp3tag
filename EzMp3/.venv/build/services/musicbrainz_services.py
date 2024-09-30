import requests
import sys
import os
import time
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
import mp3_name


song_name = mp3_name.get_first_mp3()


def get_with_retries(url, params, retries=3, delay=2):
    """Perform a request with retries in case of a 503 error."""
    for attempt in range(retries):
        response = requests.get(url, params=params)
        if response.status_code == 503:
            print(f"Error 503: Service unavailable. Retrying {attempt + 1}/{retries}...")
            time.sleep(delay)  # Wait before retrying
        else:
            return response
    print("Max retries reached. Could not fetch the data.")
    return None


def get_release_group_genres(release_group_id):
    # Fetch the release group by its ID to get genre tags
    base_url = f"https://musicbrainz.org/ws/2/release-group/{release_group_id}"
    params = {
        'fmt': 'json',
        'inc': 'tags'  # Include tags to get genres
    }
    response = get_with_retries(base_url, params)

    if response and response.status_code == 200:
        data = response.json()
        tags = data.get('tags', [])
        genres = [tag['name'] for tag in tags if tag.get('count', 0) > 0]  # Filter by relevance
        return genres
    else:
        print(f"Error fetching release group genres.")
        return []


def get_recording_genres(recording_id):
    # Fetch the recording by its ID to get genre tags as a fallback
    base_url = f"https://musicbrainz.org/ws/2/recording/{recording_id}"
    params = {
        'fmt': 'json',
        'inc': 'tags'  # Include tags to get genres directly from the recording
    }
    response = get_with_retries(base_url, params)

    if response and response.status_code == 200:
        data = response.json()
        tags = data.get('tags', [])
        genres = [tag['name'] for tag in tags if tag.get('count', 0) > 0]  # Filter by relevance
        return genres
    else:
        print(f"Error fetching recording genres.")
        return []


def search_music_metadata(query):
    base_url = "https://musicbrainz.org/ws/2/recording/"
    params = {
        'query': query,
        'fmt': 'json',
        'limit': 20
    }
    response = get_with_retries(base_url, params)

    if response and response.status_code == 200:
        data = response.json()
        results = []
        for recording in data.get('recordings', []):
            title = recording.get('title')
            artists = [artist['name'] for artist in recording['artist-credit']]
            release_info = recording.get('releases', [{}])[0]
            album = release_info.get('title')
            year = release_info.get('date', '').split('-')[0]  # Extract the year
            recording_id = recording.get('id')
            release_group_id = release_info.get('release-group', {}).get('id')

            # Try to fetch genres from the release group first
            if release_group_id:
                genres = get_release_group_genres(release_group_id)
            else:
                # Fallback to getting genres from the recording directly
                genres = get_recording_genres(recording_id)

            results.append({
                'title': title,
                'contributing_artists': artists,
                'album': album,
                'year': year,
                'genres': genres
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