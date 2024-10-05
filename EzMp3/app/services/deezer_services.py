import sys
import os
import deezer

client = deezer.Client()


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