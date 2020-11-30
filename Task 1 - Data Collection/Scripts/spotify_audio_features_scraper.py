import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import textdistance
from tqdm import tqdm

import json
import csv
import re

# Spotify API Credentials
client_id     = 'YOUR SPOTIFY ID HERE'
client_secret = 'YOUR SPOTIFY SECRET HERE' 

# Create Spotify API Session
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

# Load previously found Spotify URI data
uri_data = list(csv.reader(open("spotify_uris.csv", encoding="utf-8")))

# String comparator. Uses Levenshtein similarity for base comparation. The strings are modified in a
# variety of ways including removing a variety of combinations of special characters. The largest 
# similarity is the one that is returned.
def stringSim(word1, word2):
    base = textdistance.levenshtein.normalized_similarity(word1.lower().strip(), word2.lower().strip())
    no_spec_char = textdistance.levenshtein.normalized_similarity(re.sub(r'[^\w^ ]', '', word1.lower()).strip(), re.sub(r'[^\w^ ]', '', word2.lower()).strip())
    no_paren = textdistance.levenshtein.normalized_similarity(re.sub(r'\([^\)]*\)', '', word1.lower()).strip(), re.sub(r'\([^\)]*\)', '', word2.lower()).strip())
    no_dash = textdistance.levenshtein.normalized_similarity(re.sub(r'\-.*', '', word1.lower()).strip(), re.sub(r'\-.*', '', word2.lower()).strip())
    no_spec_no_paren = textdistance.levenshtein.normalized_similarity(re.sub(r'[^\w^ ]', '', re.sub(r'\([^\)]*\)', '', word1.lower())).strip(), re.sub(r'[^\w^ ]', '', re.sub(r'\([^\)]*\)', '', word2.lower())).strip())
    return max(base, no_spec_char, no_paren, no_dash, no_spec_no_paren)

# Load Genius data
with open('Genius Info - Billboard + MSD, 1990-2010.json', 'r') as f:
    genius_data = json.load(f)

pbar = tqdm(total=len(genius_data['songs']))
i = 0
while i < len(genius_data['songs']):
    # Build a batch of 100 song URI's to grab their audio features from Spotify
    batch_idxs = []
    batch_uris = []
    while len(batch_idxs) < 100 and i+1 < len(uri_data):
        if uri_data[i+1][4] != "NaN":
            # Get similarity between searched for and found title/artist
            title_sim = stringSim(uri_data[i+1][0], uri_data[i+1][2])
            artist_sim = stringSim(uri_data[i+1][1], uri_data[i+1][3])
            if (title_sim > .90 and artist_sim > .80) or (artist_sim > .90 and title_sim > .60):
                # If the similarity is high enough, then the found spotify URI
                # matches the Genius song we wanted. In this case, add its URI 
                # to the batch
                batch_idxs.append(i)
                batch_uris.append(uri_data[i+1][4])
                genius_data['songs'][i]['spotify_uri'] = uri_data[i+1][4]
            else:
                genius_data['songs'][i]['spotify_uri'] = 'NaN'
                genius_data['songs'][i]['audio_features'] = {}
        else:
            genius_data['songs'][i]['spotify_uri'] = 'NaN'
            genius_data['songs'][i]['audio_features'] = {}
        i += 1
        pbar.update(1)
    # Send the URI batch to Spotify API to get audio features
    batch_r = spotify.audio_features(tracks=batch_uris)

    # Update Genius data with the audio features
    for j in range(len(batch_idxs)):
        genius_data['songs'][batch_idxs[j]]['audio_features'] = batch_r[j]

# Save new dataset to a json file
with open('Spotify Features, 1990-2010.json', 'w', encoding='utf-8') as f:
    json.dump(genius_data, f)