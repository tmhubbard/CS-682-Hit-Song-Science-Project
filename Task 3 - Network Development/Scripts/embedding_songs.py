
# This script was written by Trevor Hubbard; its purpose is to create 
# "song embeddings" using the node2vec embeddings of the musicians working on them

# =========================
#        * SETUP *
# =========================

# A couple of necessary import steps
import json
import numpy as np
import pandas as pd


# Printing some information
print("\nLoading necessary files...")

# Setting up the list of the songs
datasetJsonPath = "C:\Data\College\CS 682 - Neural Networks\Project\Task 2 - Social Network Creation\Data\Genius Info - Billboard + MSD, 1990-2010.json"
songs = []
with open(datasetJsonPath, "r") as datasetJson:
	songs = json.load(datasetJson)["songs"]

# Setting up artistDict (artistID --> 10-dim embedding)
artistDict = {}
dimCount = 128
embeddingPath = "C:\Data\College\CS 682 - Neural Networks\Project\Task 3 - Network Development\Data\industryGraph - 128 dim embedding.emd"
with open(embeddingPath, "r", encoding="utf-8") as embeddingFile:
	for lineNum, line in enumerate(embeddingFile):
		if (lineNum == 0): continue
		splitLine = line.split()
		artistID = int(splitLine[0])
		artistDict[artistID] = np.array([float(x) for x in splitLine[1:]])

# Printing some information
print("Finished loading the files!")

# =========================
#       * CLASSES *
# =========================


# =========================
#       * METHODS *
# =========================

# This method will search the artistDict for each of the artists contained in the given
# song, and then return a list of [artist, artistID, artist type, embedding] lists
def retrieveArtistTuples(song):
	
	# First, retrieve all of the artists associated w/ this song
	artistTupleList = []
	if "artist" in song:
		artistInfo = song["artist"]
		artist, artistID, artistTypes = artistInfo
		artistTupleList.append([artist, artistID, artistTypes])
	if "collaborators" in song:
		for collabInfo in song["collaborators"]:
			artist, artistID, artistTypes = collabInfo
			artistTupleList.append([artist, artistID, artistTypes])

	# Now, iterate through each of the artist tuples in artistTupleList, and append
	# the respective embedding if it's there
	for artistTupleNum, artistTuple in enumerate(artistTupleList):
		artist, artistID, artistTypes = artistTuple
		if (not int(artistID) in artistDict):
			artistTupleList[artistTupleNum].append(np.zeros((dimCount,)))
		else:
			artistTupleList[artistTupleNum].append(artistDict[artistID])

	# Return the results
	return artistTupleList

# This method will average all of the artist tuples for the songs, creating an 
# "average embedding" based off of the contributors
def songEmbedding_average(song):

	# Grab the artist information from 
	artistTuples = retrieveArtistTuples(song)

	# Get a list of all of the embeddings
	embeddingList = np.array([artist[3] for artist in artistTuples])
	songEmbedding = np.sum(embeddingList, axis=0)/len(artistTuples)
	return songEmbedding

def songEmbedding_half(song):

	# Grab the artist information 
	artistTuples = retrieveArtistTuples(song)

	# Figure out which artist is the primary artist
	primaryArtistEmbedding = np.array(artistTuples[0][3])
	songEmbedding = primaryArtistEmbedding
	if (len(artistTuples) > 1):
		collaboratorEmbeddings = np.array([artist[3] for artist in artistTuples[1:]])
		collaboratorAvgEmbedding = np.sum(collaboratorEmbeddings, axis=0)/len(collaboratorEmbeddings)
		songEmbedding = (primaryArtistEmbedding + collaboratorAvgEmbedding) / 2
	return songEmbedding
	
# =========================
#        * MAIN * 
# =========================

# Printing some information
print("\nCalculating song embeddings for each song...")

songEmbedder = songEmbedding_average
embeddingType = "half"
if (embeddingType == "half"):
	songEmbedder = songEmbedding_half

songList = []
for songNum, song in enumerate(songs):
	
	if (songNum % 1000 == 0): 
		print("Calculating embedding for song %d..." % songNum)

	songTitle, songID = song["title"]
	artist = song["artist"][0]
	artistID = song["artist"][1]
	hit = 0
	if (song["hit"] == True):
		hit = 1
	embedding = songEmbedder(song)
	if (np.array_equal(embedding,np.zeros(dimCount))):
		embedding += -10
	songList.append([songTitle, songID, artist, artistID, hit] + [x for x in list(embedding)])

columnNames = ["title", "songID", "artist", "artistID", "hit"] + [("emb_dim_%d" % embNum) for embNum in range(len(embedding))]
songDF = pd.DataFrame(songList, columns=columnNames)
saveName = "../Data/Song Embeddings - " + str(dimCount) + " dim (" + embeddingType + ").xlsx"
print("\nSaving the song embeddings to disk...")
songDF.to_excel(saveName)
print("Finished saving the embeddings!")