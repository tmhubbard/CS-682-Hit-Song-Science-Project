import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm

import json
import csv
import re

client_id     = 'YOUR SPOTIFY ID HERE'
client_secret = 'YOUR SPOTIFY SECRET HERE' 

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

data = list(csv.reader(open("spotify_uris.csv", encoding="utf-8")))

for i in tqdm(range(1, len(data))):
    row = data[i]
    if row[4] == "NaN":
        title  = re.sub(r'[^\w^ ]', '', re.sub(r'\([^\)]*\)', '', row[0].lower())).strip()
        artist = re.sub(r'[^\w^ ]', '', re.sub(r'\([^\)]*\)', '', row[1].lower())).strip()
        q = "artist:{} track:{}".format(artist, title)
        r = spotify.search(q, type='track', limit=1)
        try:
            found_title  = r['tracks']['items'][0]['name']
            found_artist = r['tracks']['items'][0]['artists'][0]['name']
            found_uri    = r['tracks']['items'][0]['uri']
        except (IndexError, KeyError) as e:
            found_title  = "NaN"
            found_artist = "NaN"
            found_uri    = "NaN"
        row[2] = found_title
        row[3] = found_artist
        row[4] = found_uri
        data[i] = row

with open("spotify_uris2.csv", "w", newline="", encoding="utf-8") as f:
    csv.writer(f, delimiter=',').writerows(data)