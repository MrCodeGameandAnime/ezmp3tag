import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TPE1, TPE2, TALB, TYER, TCON
import logging
from EzMp3.app.utils.mp3_name import extract_mp3_name  # Importing the function to get the MP3 name

# Set up logging
logging.basicConfig(level=logging.INFO)


def change_mp3_metadata(file_path, new_title, new_contributing_artist, new_album_artist, new_album, new_year,
                        new_genre):
    # Check if the file exists
    if not os.path.isfile(file_path):
        logging.error(f"File '{file_path}' does not exist.")
        return

    try:
        # Load the MP3 file
        audio = MP3(file_path, ID3=ID3)

        # Set the ID3 tags
        if audio.tags is None:
            audio.add_tags()  # Create tags if they don't exist

        # Update the tags if they already exist or add them if not
        audio.tags["TIT2"] = TIT2(encoding=3, text=new_title)  # Title
        audio.tags["TPE1"] = TPE1(encoding=3, text=new_contributing_artist)  # Contributing Artist
        audio.tags["TPE2"] = TPE2(encoding=3, text=new_album_artist)  # Album Artist
        audio.tags["TALB"] = TALB(encoding=3, text=new_album)  # Album
        audio.tags["TYER"] = TYER(encoding=3, text=str(new_year))  # Year
        audio.tags["TCON"] = TCON(encoding=3, text=new_genre)  # Genre

        # Save changes
        audio.save()
        logging.info(f"Successfully updated '{file_path}' with new metadata.")

    except ID3NoHeaderError:
        logging.warning("No ID3 header found. Adding one now.")
        audio.add_tags()
        audio.tags["TIT2"] = TIT2(encoding=3, text=new_title)
        audio.tags["TPE1"] = TPE1(encoding=3, text=new_contributing_artist)
        audio.tags["TPE2"] = TPE2(encoding=3, text=new_album_artist)
        audio.tags["TALB"] = TALB(encoding=3, text=new_album)
        audio.tags["TYER"] = TYER(encoding=3, text=str(new_year))
        audio.tags["TCON"] = TCON(encoding=3, text=new_genre)
        audio.save()
        logging.info(f"Successfully added ID3 tags to '{file_path}' with new metadata.")

    except Exception as e:
        logging.error(f"An error occurred while updating metadata: {e}")


if __name__ == "__main__":
    # Get the MP3 file name dynamically
    mp3_name = extract_mp3_name()  # This will return the first MP3 file name in the directory
    if mp3_name:
        mp3_dir = os.getenv("MP3_DIR")

        if mp3_dir:
            mp3_file_path = os.path.join(mp3_dir, f"{mp3_name}.mp3")

            new_title = "New Song Title"
            new_contributing_artist = "Contributing Artist"
            new_album_artist = "Album Artist"
            new_album = "Album Name"
            new_year = 2024
            new_genre = "Pop"

            change_mp3_metadata(mp3_file_path, new_title, new_contributing_artist, new_album_artist, new_album,
                                new_year, new_genre)
        else:
            logging.error("MP3_DIR environment variable is not set.")
    else:
        logging.error("No MP3 file found.")
