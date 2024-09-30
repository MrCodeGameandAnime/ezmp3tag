import sys
import os
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
import mp3_name
import deezer

client = deezer.Client()

# Search for a track by title
search_query = mp3_name.get_first_mp3()
results = client.search(search_query)

# Display results
# for track in results:
#     # Print track information
#     print(f"Title: {track.title}")
#     print(f"Contributing Artist(s): {[artist.name for artist in track.contributors]}")
#     print(f"Album Artist: {track.artist.name}")
#     print(f"Album: {track.album.title}")
#
#     # Check if release_date is available
#     if track.album.release_date:
#         # Format the release_date to get the year
#         release_year = track.album.release_date.strftime("%Y")
#         print(f"Year: {release_year}")
#     else:
#         print("Year: Not Available")
#
#     # Deezer API does not provide a direct 'genre' attribute for a track
#     if track.album.genres:
#         print(f"Genre: {track.album.genres[0].name}")
#     else:
#         print("Genre: Not Available")
#
#     print("-" * 40)


def fetch_deezer_metadata(track_name):
    """Fetch metadata from Deezer for a given track name."""
    try:
        # Search for the track by title
        results = client.search(track_name)

        # Filter for non-compilation albums
        filtered_tracks = []
        for track in results:
            if track.album and 'compilation' not in track.album.title.lower():
                filtered_tracks.append(track)

        # Prioritize the earliest release
        earliest_track = None
        for track in filtered_tracks:
            if earliest_track is None or (track.album.release_date and track.album.release_date < earliest_track.album.release_date):
                earliest_track = track

        if earliest_track:
            # Prepare metadata to return
            release_year = earliest_track.album.release_date.strftime("%Y") if earliest_track.album.release_date else "Not Available"
            return {
                'title': earliest_track.title,
                'contributing_artists': [artist.name for artist in earliest_track.contributors],
                'album_artist': earliest_track.artist.name,
                'album': earliest_track.album.title,
                'year': release_year,
                'genres': [genre.name for genre in earliest_track.album.genres] if earliest_track.album.genres else []
            }
    except Exception as e:
        print(f"Deezer error: {e}")
    return None