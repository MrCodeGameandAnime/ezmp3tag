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
for track in results:
    # Print track information
    print(f"Title: {track.title}")
    print(f"Contributing Artist(s): {[artist.name for artist in track.contributors]}")
    print(f"Album Artist: {track.artist.name}")
    print(f"Album: {track.album.title}")

    # Check if release_date is available
    if track.album.release_date:
        # Format the release_date to get the year
        release_year = track.album.release_date.strftime("%Y")
        print(f"Year: {release_year}")
    else:
        print("Year: Not Available")

    # Deezer API does not provide a direct 'genre' attribute for a track
    if track.album.genres:
        print(f"Genre: {track.album.genres[0].name}")
    else:
        print("Genre: Not Available")

    print("-" * 40)