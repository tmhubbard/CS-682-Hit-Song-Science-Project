
# This script was written by Trevor Hubbard; its purpose is to add information 
# from the "metatdata" tab of the .h5 file to the .xlsx of songs

# =========================
#        * SETUP *
# =========================

# Some import statements
import h5py
import time
import numpy as np
import pandas as pd
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

# Set up some variables to collect song information
metadata_columnTitles = ["analyzer_version","artist_7digitalid","artist_familiarity","artist_hotttnesss","artist_id","artist_latitude","artist_location","artist_longitude","artist_mbid","artist_name","artist_playmeid","genre","idx_artist_terms","idx_similar_artists","release","release_7digitalid","song_hotttnesss","song_id","title","track_7digitalid"]
analysis_columnTitles = ['analysis_sample_rate','audio_md5','danceability','duration','end_of_fade_in','energy','idx_bars_confidence','idx_bars_start','idx_beats_confidence','idx_beats_start','idx_sections_confidence','idx_sections_start','idx_segments_confidence','idx_segments_loudness_max','idx_segments_loudness_max_time','idx_segments_loudness_start','idx_segments_pitches','idx_segments_start','idx_segments_timbre','idx_tatums_confidence','idx_tatums_start','key','key_confidence','loudness','mode','mode_confidence','start_of_fade_out','tempo','time_signature','time_signature_confidence','track_id', 'title', 'artist', 'year', 'songID']
songDict = {}
for title in analysis_columnTitles:
	songDict[title] = []

# Making a DataFrame from the songs with years
oldTime = time.time()
print("Starting to read in the Excel...")
with open("songsWithYears.csv", "r", encoding="utf-8") as songsWithYearsFile:
	for line in songsWithYearsFile:
		splitLine = line.strip().split(",")
		for entryNum, entry in enumerate(splitLine):
			songDict[analysis_columnTitles[entryNum]].append(entry)
songsWithYearsDF = pd.DataFrame.from_dict(songDict)
print("It took %.2f sec to read in the Excel file" % (time.time()-oldTime))
print(songsWithYearsDF)

# Step through each of the songs in the metadata_songsGroup
songsAdded = 0
newSongDict = {}
for title in metadata_columnTitles:
	if (title == "title"): continue
	newSongDict[title] = []
for title in analysis_columnTitles:
	newSongDict[title] = []
for songNum, song in enumerate(metadata_songsGroup):

	# Grab some information about the current song
	songID = song[17].decode("utf-8")

	# Check if there's information for the current song
	try:
		songRow = songsWithYearsDF.loc[songsWithYearsDF['songID'] == songID]
	except KeyError:
		continue

	# Skip if there's no information for the current song
	if (songRow.empty):
		continue

	# Add all of the values from the analysis database
	headerList = list(songRow)
	for header in headerList:
		if (header == "title"): continue
		newSongDict[header].append(songRow[header].values[0])

	# Cast each entry in the row as a particular type 
	for entryIdx, entry in enumerate(list(song)):
		convertedEntry = -1
		if (type(entry) is np.bytes_):
			convertedEntry = (entry.decode("utf-8"))
		elif (type(entry) is np.int32):
			convertedEntry = (int(entry))
		elif (type(entry) is np.float64):
			convertedEntry = (float(entry))

		# Add the converted entry to its correct row
		newSongDict[metadata_columnTitles[entryIdx]].append(convertedEntry)

	# Increment count
	songsAdded += 1
	if ((songsAdded % 100) == 0):
		print("%d songs added" % songsAdded)

	if (songsAdded % 100000 == 0):
		newSongDF = pd.DataFrame.from_dict(newSongDict)
		newSongDF.to_excel("result.xlsx", engine="xlsxwriter")

# Create the DataFrame from it 
newSongDF = pd.DataFrame.from_dict(newSongDict)
newSongDF.to_excel("result.xlsx", engine="xlsxwriter")