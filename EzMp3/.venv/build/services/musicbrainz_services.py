import requests
import sys
import os
import time
import musicbrainzngs
from datetime import datetime


musicbrainzngs.set_useragent("EzMP3Tags", "1.0", "https://EzMP3tags.com")


def fetch_musicbrainz_metadata(track):
    """Fetch metadata from MusicBrainz using only track name, prioritize original studio album."""
    try:
        result = musicbrainzngs.search_recordings(recording=track, limit=10)  # Fetch up to 10 results
        #print("Raw MusicBrainz Response:", result)  # Debugging line
        earliest_album = None

        for recording in result.get('recording-list', []):
            release_list = recording.get('release-list', [])
            for release in release_list:
                # Ensure it's an official, non-compilation album
                if 'status' in release and release['status'] == 'Official':
                    secondary_types = release.get('secondary-type-list', [])
                    if "compilation" not in secondary_types and "soundtrack" not in secondary_types:
                        release_date = release.get('date')

                        if release_date:
                            try:
                                # Parse the date into a datetime object
                                release_date_obj = datetime.strptime(release_date, "%Y-%m-%d")
                            except ValueError:
                                try:
                                    # Handle cases where only the year is present
                                    release_date_obj = datetime.strptime(release_date, "%Y")
                                except ValueError:
                                    print(f"Invalid date format for release: {release_date}")
                                    continue
                        else:
                            print("No date available for this release.")
                            continue

                        # Compare the current album with the earliest found album
                        if earliest_album is None or release_date_obj < earliest_album['release_date_obj']:
                            earliest_album = {
                                'title': release['title'],
                                'artist_credit': release.get('artist-credit', [{}])[0],
                                'date': release_date,
                                'release_date_obj': release_date_obj
                            }

        if earliest_album:
            return {
                'title': recording['title'],
                'artist': recording['artist-credit'][0]['artist']['name'],
                'album': earliest_album['title'],
                'album_artist': earliest_album['artist_credit'].get('artist', {}).get('name'),
                'year': earliest_album['date'][:4] if 'date' in earliest_album else None,
            }
        else:
            print("No suitable album found for the track.")
            return None

    except Exception as e:
        print(f"MusicBrainz error: {e}")
        return None

# def get_with_retries(url, params, retries=3, delay=2):
#     """Perform a request with retries in case of a 503 error."""
#     for attempt in range(retries):
#         response = requests.get(url, params=params)
#         if response.status_code == 503:
#             print(f"Error 503: Service unavailable. Retrying {attempt + 1}/{retries}...")
#             time.sleep(delay)  # Wait before retrying
#         else:
#             return response
#     print("Max retries reached. Could not fetch the data.")
#     return None
#
#
# def get_release_group_genres(release_group_id):
#     # Fetch the release group by its ID to get genre tags
#     base_url = f"https://musicbrainz.org/ws/2/release-group/{release_group_id}"
#     params = {
#         'fmt': 'json',
#         'inc': 'tags'  # Include tags to get genres
#     }
#     response = get_with_retries(base_url, params)
#
#     if response and response.status_code == 200:
#         data = response.json()
#         tags = data.get('tags', [])
#         genres = [tag['name'] for tag in tags if tag.get('count', 0) > 0]  # Filter by relevance
#         return genres
#     else:
#         print(f"Error fetching release group genres.")
#         return []
#
#
# def get_recording_genres(recording_id):
#     # Fetch the recording by its ID to get genre tags as a fallback
#     base_url = f"https://musicbrainz.org/ws/2/recording/{recording_id}"
#     params = {
#         'fmt': 'json',
#         'inc': 'tags'  # Include tags to get genres directly from the recording
#     }
#     response = get_with_retries(base_url, params)
#
#     if response and response.status_code == 200:
#         data = response.json()
#         tags = data.get('tags', [])
#         genres = [tag['name'] for tag in tags if tag.get('count', 0) > 0]  # Filter by relevance
#         return genres
#     else:
#         print(f"Error fetching recording genres.")
#         return []
#
#
# def search_music_metadata(query):
#     base_url = "https://musicbrainz.org/ws/2/recording/"
#     params = {
#         'query': query,
#         'fmt': 'json',
#         'limit': 20
#     }
#     response = get_with_retries(base_url, params)
#
#     if response and response.status_code == 200:
#         data = response.json()
#         results = []
#         for recording in data.get('recordings', []):
#             title = recording.get('title')
#             artists = [artist['name'] for artist in recording['artist-credit']]
#             release_info = recording.get('releases', [{}])[0]
#             album = release_info.get('title')
#             year = release_info.get('date', '').split('-')[0]  # Extract the year
#             recording_id = recording.get('id')
#             release_group_id = release_info.get('release-group', {}).get('id')
#
#             # Try to fetch genres from the release group first
#             if release_group_id:
#                 genres = get_release_group_genres(release_group_id)
#             else:
#                 # Fallback to getting genres from the recording directly
#                 genres = get_recording_genres(recording_id)
#
#             results.append({
#                 'title': title,
#                 'contributing_artists': artists,
#                 'album': album,
#                 'year': year,
#                 'genres': genres
#             })
#         return results
#     else:
#         print(f"Error: {response.status_code}")
#         return None
#
#
# # Example usage
# query = song_name
# metadata = search_music_metadata(query)
# for result in metadata:
#     print(result)

