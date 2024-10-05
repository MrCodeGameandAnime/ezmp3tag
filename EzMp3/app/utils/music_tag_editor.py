import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TPE1, TPE2, TALB, TYER, TCON
from .mp3_name import extract_mp3_name  # Importing the function to get the MP3 name


def change_mp3_metadata(file_path, new_title, new_contributing_artist, new_album_artist, new_album, new_year,
                        new_genre):
    # Check if the file exists
    if not os.path.isfile(file_path):
        print(f"File '{file_path}' does not exist.")
        return

    try:
        # Load the MP3 file
        audio = MP3(file_path, ID3=ID3)

        # Set the ID3 tags
        if audio.tags is None:
            audio.add_tags()  # Create tags if they don't exist

        audio.tags.add(TIT2(encoding=3, text=new_title))  # Title
        audio.tags.add(TPE1(encoding=3, text=new_contributing_artist))  # Contributing Artist
        audio.tags.add(TPE2(encoding=3, text=new_album_artist))  # Album Artist
        audio.tags.add(TALB(encoding=3, text=new_album))  # Album
        audio.tags.add(TYER(encoding=3, text=str(new_year)))  # Year
        audio.tags.add(TCON(encoding=3, text=new_genre))  # Genre

        # Save changes
        audio.save()
        print(f"Successfully updated '{file_path}' with new metadata.")

    except ID3NoHeaderError:
        print("No ID3 header found. Adding one now.")
        audio.add_tags()
        audio.tags.add(TIT2(encoding=3, text=new_title))
        audio.tags.add(TPE1(encoding=3, text=new_contributing_artist))
        audio.tags.add(TPE2(encoding=3, text=new_album_artist))
        audio.tags.add(TALB(encoding=3, text=new_album))
        audio.tags.add(TYER(encoding=3, text=str(new_year)))
        audio.tags.add(TCON(encoding=3, text=new_genre))
        audio.save()
        print(f"Successfully added ID3 tags to '{file_path}' with new metadata.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # Get the MP3 file name dynamically
    mp3_name = extract_mp3_name()  # This will return the first MP3 file name in the directory
    if mp3_name:
        mp3_file_path = os.path.join(os.getenv("MP3_DIR"), f"{mp3_name}.mp3")

        new_title = "New Song Title"
        new_contributing_artist = "Contributing Artist"
        new_album_artist = "Album Artist"
        new_album = "Album Name"
        new_year = 2024
        new_genre = "Pop"

        change_mp3_metadata(mp3_file_path, new_title, new_contributing_artist, new_album_artist, new_album, new_year,
                            new_genre)
