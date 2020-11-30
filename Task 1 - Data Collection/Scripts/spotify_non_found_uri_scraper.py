import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm

import json
import csv
import re

# Spotify API Credentials
client_id     = 'YOUR SPOTIFY ID HERE'
client_secret = 'YOUR SPOTIFY SECRET HERE' 

# Create Spotify API Session
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

# Open previously scraped URI info
data = list(csv.reader(open("spotify_uris.csv", encoding="utf-8")))

for i in tqdm(range(1, len(data))):
    row = data[i]

    # If song URI search previously found nothing
    if row[4] == "NaN":

        # Strip song title/artist of parenthesis phrases and non-word characters
        title  = re.sub(r'[^\w^ ]', '', re.sub(r'\([^\)]*\)', '', row[0].lower())).strip()
        artist = re.sub(r'[^\w^ ]', '', re.sub(r'\([^\)]*\)', '', row[1].lower())).strip()
        
        # Build and send search query
        q = "artist:{} track:{}".format(artist, title)
        r = spotify.search(q, type='track', limit=1)
        try:
            # Expand search result
            found_title  = r['tracks']['items'][0]['name']
            found_artist = r['tracks']['items'][0]['artists'][0]['name']
            found_uri    = r['tracks']['items'][0]['uri']
        except (IndexError, KeyError) as e:
            found_title  = "NaN"
            found_artist = "NaN"
            found_uri    = "NaN"
        # Update song info with new search results
        row[2] = found_title
        row[3] = found_artist
        row[4] = found_uri
        data[i] = row

# Save search results to a csv file
with open("spotify_uris2.csv", "w", newline="", encoding="utf-8") as f:
    csv.writer(f, delimiter=',').writerows(data)