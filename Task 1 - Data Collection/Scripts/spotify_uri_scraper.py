import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from tqdm import tqdm

import json
import csv

# Spotify API Info
client_id     = 'YOUR SPOTIFY ID HERE'
client_secret = 'YOUR SPOTIFY SECRET HERE' 

# Create Spotify API Session
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

with open('Genius Info - Billboard + MSD, 1990-2010.json', 'r') as f:
    data = json.load(f)

result = [['title', 'artist', 'found_title', 'found_artist', 'found_uri', 'hit']]

# Iterate over songs in Genius Info
for i in tqdm(range(len(data['songs']))):
    song = data['songs'][i]
    title = song['title'][0]
    artist = song['artist'][0]

    # Form and send search query for song
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
    # Add song search results to list
    result.append([title, artist, found_title, found_artist, found_uri, str(song['hit'])])

# Write the search results to a csv file
with open("spotify_uris.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerows(result)