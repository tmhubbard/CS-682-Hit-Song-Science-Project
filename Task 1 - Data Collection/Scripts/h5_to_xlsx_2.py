
# This script was written by Trevor Hubbard; its purpose is to convert .hdf5
# files to .xlsx, because I didn't want to download HDFView. (Chrome was 
# warning about a virus, sooooooo)

# =========================
#        * SETUP *
# =========================

# Some import statements
import h5py
import numpy as np
import pandas as pd
from time import sleep
from pathlib import Path


# =========================
#        * MAIN * 
# =========================

# Setting up the Database
h5FilePath = Path("msd_summary_file.h5")
h5File = h5py.File(h5FilePath, "r")
metadataGroup = h5File["/metadata/"]
musicbrainzGroup = h5File["/musicbrainz/"]
analysisGroup = h5File["/analysis/"]
metadata_songsGroup = h5File["/metadata/songs/"]
musicbrainz_songsGroup = h5File["/musicbrainz/songs/"]
analysis_songsGroup = h5File["/analysis/songs/"]


# Setting up the track-year dict
trackYearDict_trackID = {}
with open("tracks_per_year.txt", "r", encoding="utf-8") as trackYearFile:
	for line in trackYearFile:
		year, trackID, artist, title = line.split("<SEP>")
		year = year.strip()
		trackID = trackID.strip()
		artist = artist.strip()
		title = title.strip()
		trackYearDict_trackID[trackID] = (year, artist, title)

# Setting up the trackSongID dict
trackSongIDDict = {}
with open("unique_tracks.txt", "r", encoding="utf-8") as trackSongIDFile:
	for line in trackSongIDFile:
		trackID, songID, artist, title = line.split("<SEP>")
		trackID = trackID.strip()
		songID = songID.strip()
		trackSongIDDict[trackID] = songID

# Set up some variables to collect song information
metadata_columnTitles = ["analyzer_version","artist_7digitalid","artist_familiarity","artist_hotttnesss","artist_id","artist_latitude","artist_location","artist_longitude","artist_mbid","artist_name","artist_playmeid","genre","idx_artist_terms","idx_similar_artists","release","release_7digitalid","song_hotttnesss","song_id","title","track_7digitalid"]
analysis_columnTitles = ['analysis_sample_rate','audio_md5','danceability','duration','end_of_fade_in','energy','idx_bars_confidence','idx_bars_start','idx_beats_confidence','idx_beats_start','idx_sections_confidence','idx_sections_start','idx_segments_confidence','idx_segments_loudness_max','idx_segments_loudness_max_time','idx_segments_loudness_start','idx_segments_pitches','idx_segments_start','idx_segments_timbre','idx_tatums_confidence','idx_tatums_start','key','key_confidence','loudness','mode','mode_confidence','start_of_fade_out','tempo','time_signature','time_signature_confidence','track_id', 'title', 'artist', 'year', 'songID']
songDict = {}
for title in analysis_columnTitles:
	songDict[title] = []

# Step through each of the songs in the metadata_songsGroup
songsAdded = 0
for song in analysis_songsGroup:

	# Grab some information about the current song
	trackID = song[30].decode("utf-8")

	# Check if there's year information for the current track
	if (not trackID in trackYearDict_trackID):
		continue

	# Get more information about the song from other dicts
	songYear, songArtist, songTitle = trackYearDict_trackID[trackID]
	songID = trackSongIDDict[trackID]

	# Set up variables to store the info from this song
	listSong = list(song)
	decodedSong = []

	# Cast each entry in the row as a particular type
	for entryIdx, entry in enumerate(listSong):
		convertedEntry = -1
		if (type(entry) is np.bytes_):
			convertedEntry = (entry.decode("utf-8"))
		elif (type(entry) is np.int32):
			convertedEntry = (int(entry))
		elif (type(entry) is np.float64):
			convertedEntry = (float(entry))

		# Add the converted entry to its correct row
		songDict[analysis_columnTitles[entryIdx]].append(convertedEntry)

	songDict['title'].append(songTitle)
	songDict['artist'].append(songArtist)
	songDict['year'].append(songYear)
	songDict['songID'].append(songID)

	# Increment count
	songsAdded += 1
	if ((songsAdded % 100) == 0):
		print("%d songs added" % songsAdded)

# Create the DataFrame from it 
songDF = pd.DataFrame.from_dict(songDict)
songDF.to_excel("result.xlsx", engine="xlsxwriter")
