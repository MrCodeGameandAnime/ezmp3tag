import json
import os
import sys
from urllib import request
from urllib.parse import parse_qsl
import oauth2 as oauth
from dotenv import load_dotenv
import pickle

load_dotenv()

consumer_key = os.getenv('CONSUMER_KEY')
consumer_secret = os.getenv('CONSUMER_SECRET')

request_token_url = "https://api.discogs.com/oauth/request_token"
authorize_url = "https://www.discogs.com/oauth/authorize"
access_token_url = "https://api.discogs.com/oauth/access_token"

user_agent = "ezmp3/1.0"
token_file = 'discogs_token.pkl'

def get_request_token():
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)
    resp, content = client.request(request_token_url, "POST", headers={"User-Agent": user_agent})

    if resp["status"] != "200":
        sys.exit(f"Invalid response {resp['status']}")

    return dict(parse_qsl(content.decode("utf-8")))

def authorize_request(request_token):
    print(f"Please visit the following URL to authorize: {authorize_url}?oauth_token={request_token['oauth_token']}")
    authorized = input("Have you authorized the app? [y/n]: ")

    # Normalize user input to lowercase for comparison
    if authorized.lower() in ["y", "yes"]:
        oauth_verifier = input("Enter the verification code: ")
        return oauth_verifier
    else:
        sys.exit("Authorization not completed.")

def get_access_token(request_token, oauth_verifier):
    token = oauth.Token(request_token["oauth_token"], request_token["oauth_token_secret"])
    token.set_verifier(oauth_verifier)
    client = oauth.Client(oauth.Consumer(consumer_key, consumer_secret), token)
    resp, content = client.request(access_token_url, "POST", headers={"User-Agent": user_agent})

    if resp["status"] != "200":
        sys.exit(f"Invalid response {resp['status']}")

    return dict(parse_qsl(content.decode("utf-8")))

def load_access_token():
    """Load access token from a file if it exists."""
    if os.path.exists(token_file):
        with open(token_file, 'rb') as f:
            return pickle.load(f)
    return None

def save_access_token(access_token):
    """Save access token to a file."""
    with open(token_file, 'wb') as f:
        pickle.dump(access_token, f)

def search_discogs(access_token, song_name):
    token = oauth.Token(key=access_token["oauth_token"], secret=access_token["oauth_token_secret"])
    client = oauth.Client(oauth.Consumer(consumer_key, consumer_secret), token)

    search_params = f"release_title={song_name.replace(' ', '+')}"
    search_query = f'https://api.discogs.com/database/search?{search_params}'
    resp, content = client.request(search_query, headers={"User-Agent": user_agent})

    if resp["status"] != "200":
        sys.exit(f"Invalid API response {resp['status']}")

    results = json.loads(content.decode("utf-8"))
    filtered_results = []

    # Filtering for official non-compilation albums
    for release in results.get("results", []):
        if 'compilation' not in release.get('type', '') and 'album' in release.get('type', ''):
            filtered_results.append({
                'id': release["id"],
                'title': release.get("title", "Unknown"),
                'artist': release.get("artist", ["Unknown"]),
                'album_artist': release.get("album_artist", ["Unknown"]),
                'year': release.get("year", "Unknown"),
                'genre': release.get("genre", ["Unknown"])
            })

    return filtered_results

def print_discogs_results(results):
    print("\n== Discogs Search Results ==")
    for release in results:
        print(f'\n\t== Discogs ID: {release["id"]} ==')
        print(f'\tTitle\t\t: {release["title"]}')
        print(f'\tContributing Artist\t: {", ".join(release["artist"])}')
        print(f'\tAlbum Artist\t: {", ".join(release["album_artist"])}')
        print(f'\tYear\t\t: {release["year"]}')
        print(f'\tGenre\t\t: {", ".join(release["genre"])}')

def get_discogs_metadata(song_name):
    """Get Discogs metadata for a song."""
    access_token = load_access_token()

    # If no access token is found, go through the OAuth process
    if access_token is None:
        request_token = get_request_token()
        oauth_verifier = authorize_request(request_token)
        access_token = get_access_token(request_token, oauth_verifier)
        save_access_token(access_token)  # Save the new access token

    return search_discogs(access_token, song_name)

if __name__ == "__main__":
    song_name = "Your Song Name Here"  # Replace with an actual song name for testing
    discogs_results = get_discogs_metadata(song_name)
    print_discogs_results(discogs_results)
