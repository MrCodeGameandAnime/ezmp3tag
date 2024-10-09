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
        # print("Raw MusicBrainz Response:", result)  # Debugging line
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
