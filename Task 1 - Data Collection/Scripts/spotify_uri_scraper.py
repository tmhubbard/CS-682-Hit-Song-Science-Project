import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm

import json
import csv

client_id     = 'YOUR SPOTIFY ID HERE'
client_secret = 'YOUR SPOTIFY SECRET HERE' 

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

with open('Genius Info - Billboard + MSD, 1990-2010.json', 'r') as f:
    data = json.load(f)

result = [['title', 'artist', 'found_title', 'found_artist', 'found_uri', 'hit']]

for i in tqdm(range(len(data['songs']))):
    song = data['songs'][i]
    title = song['title'][0]
    artist = song['artist'][0]
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
    result.append([title, artist, found_title, found_artist, found_uri, str(song['hit'])])

with open("spotify_uris.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerows(result)