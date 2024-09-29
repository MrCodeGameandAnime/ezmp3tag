#!/usr/bin/env python

import json
import sys
from urllib import request
from urllib.parse import parse_qsl
import oauth2 as oauth
import GatherFileNames

consumer_key = "wutlrVtzfmEhQFSNQJlC"
consumer_secret = "RojkMIvZhSHjIabnfxyqTnOZAfyNoJbH"

request_token_url = "https://api.discogs.com/oauth/request_token"
authorize_url = "https://www.discogs.com/oauth/authorize"
access_token_url = "https://api.discogs.com/oauth/access_token"

user_agent = "ezmp3/1.0"
song_name = GatherFileNames.get_file_name()
print(song_name)


def get_request_token():
    consumer = oauth.Consumer(consumer_key, consumer_secret)
    client = oauth.Client(consumer)
    resp, content = client.request(
        request_token_url, "POST", headers={"User-Agent": user_agent}
    )

    if resp["status"] != "200":
        sys.exit(f"Invalid response {resp['status']}")

    return dict(parse_qsl(content.decode("utf-8")))


def authorize_request(request_token):
    print(f"Please visit the following URL to authorize: {authorize_url}?oauth_token={request_token['oauth_token']}")
    authorized = input("Have you authorized the app? [y/n]: ")
    if authorized.lower() == "y":
        oauth_verifier = input("Enter the verification code: ")
        return oauth_verifier
    else:
        sys.exit("Authorization not completed.")


def get_access_token(request_token, oauth_verifier):
    token = oauth.Token(request_token["oauth_token"], request_token["oauth_token_secret"])
    token.set_verifier(oauth_verifier)
    client = oauth.Client(oauth.Consumer(consumer_key, consumer_secret), token)
    resp, content = client.request(
        access_token_url, "POST", headers={"User-Agent": user_agent}
    )

    if resp["status"] != "200":
        sys.exit(f"Invalid response {resp['status']}")

    return dict(parse_qsl(content.decode("utf-8")))


def search_discogs(access_token, search_params):
    token = oauth.Token(
        key=access_token["oauth_token"], secret=access_token["oauth_token_secret"]
    )
    client = oauth.Client(oauth.Consumer(consumer_key, consumer_secret), token)

    search_query = f'https://api.discogs.com/database/search?{search_params}'
    resp, content = client.request(search_query, headers={"User-Agent": user_agent})

    if resp["status"] != "200":
        sys.exit(f"Invalid API response {resp['status']}")

    results = json.loads(content.decode("utf-8"))
    print("\n== Search Results ==")
    for release in results["results"]:
        print(f'\n\t== discogs-id {release["id"]} ==')
        print(f'\tTitle\t: {release.get("title", "Unknown")}')
        print(f'\tYear\t: {release.get("year", "Unknown")}')
        print(f'\tLabels\t: {", ".join(release.get("label", ["Unknown"]))}')
        print(f'\tCat No\t: {release.get("catno", "Unknown")}')
        print(f'\tFormats\t: {", ".join(release.get("format", ["Unknown"]))}')

if __name__ == "__main__":
    # Step 1: Get request token
    request_token = get_request_token()

    # Step 2: Authorize request
    oauth_verifier = authorize_request(request_token)

    # Step 3: Get access token
    access_token = get_access_token(request_token, oauth_verifier)

    # Step 4: Use search function
    search_params = f"release_title={song_name}"
    search_discogs(access_token, search_params)