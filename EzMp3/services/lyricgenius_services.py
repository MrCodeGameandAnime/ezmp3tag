import lyricsgenius
'''Need a website to include this api'''
# Replace with your Genius API Access Token
genius = lyricsgenius.Genius("your_genius_access_token")


def search_song_info(song_title):
    # Search for a song by title
    song = genius.search_song(song_title)

    if song:
        song_info = {
            "title": song.title,
            "contributing_artist": song.artist,
            "album": song.album,
            "year": song.year,
            # Genius doesn't provide genre directly, you'll need to use a different API for genre.
        }
        return song_info
    else:
        return None


# Example Usage
song_title = "Lose Yourself"
song_info = search_song_info(song_title)

if song_info:
    print(f"Title: {song_info['title']}")
    print(f"Contributing Artist: {song_info['contributing_artist']}")
    print(f"Album: {song_info['album']}")
    print(f"Year: {song_info['year']}")
else:
    print("Song not found.")