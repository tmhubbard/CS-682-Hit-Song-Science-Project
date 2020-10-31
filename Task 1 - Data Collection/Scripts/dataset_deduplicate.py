
# This script was written by Trevor Hubbard; its purpose is to merge together
# (and deduplicate) the different files in the dataset

# =========================
#        * SETUP *
# =========================

# Some import statements
import json
from pathlib import Path

# Setup the folder to the cleaned data
datasetPath = Path("C:\Data\Personal Study\Datasets\Full Genius Dataset - Validated, Cleaned with features")

# =========================
#       * METHODS *
# =========================

# This method will convert a JSON object to a formatted string
def jprint(jsonObject):
	print((json.dumps(jsonObject, sort_keys = True, indent = 4)))

# This method will merge a list of duplicate records into one record
def mergeDuplicates(duplicateList):

	# Create a new dict for the merged song
	mergedDict = {"title": (),
			      "artist": (),
			   	  "collaborators": [],
			      "year": "<NONE>",
			      "hit": False,
			      "billboard_uid": [],
			      "msd_uid": []}

	# Add the UIDs to the mergedDict, and change hit
	for duplicate in duplicateList:
		if (duplicate["hit"] == True):
			mergedDict["hit"] = True
		if (not duplicate["billboard_uid"] == "<NONE>"):
			if (not duplicate["billboard_uid"] in mergedDict["billboard_uid"]):
				mergedDict["billboard_uid"].append(duplicate["billboard_uid"])
		if (not duplicate["msd_uid"] == "<NONE>"):
			if (not duplicate["msd_uid"] in mergedDict["msd_uid"]):
				mergedDict["msd_uid"].append(duplicate["msd_uid"])
		if (not duplicate["year"] == "<NONE>"):
			mergedDict["year"] = duplicate["year"]

	# Update the rest of the attributes in mergedDict w/ the first duplicate's info
	firstDup = duplicateList[0]
	mergedDict["title"] = firstDup["title"]
	mergedDict["artist"] = firstDup["artist"]
	mergedDict["collaborators"] = firstDup["collaborators"]

	# Return the merged dict
	return mergedDict

# =========================
#        * MAIN * 
# =========================

# Creating a dict of (songID, songDict) pairs 
masterSongDict = {}
duplicateIDList = []

# Iterating through all of the .json files in the dataset
curSong = 0
duplicateCount = 0
print("\nIterating through each song and checking if it's a duplicate...\n")
for songJsonPath in datasetPath.iterdir():

	curSong += 1
	if (curSong % 5000 == 0):
		print("Finished %d songs" % (curSong))

	# Load the .json's data into songDict
	songDict = {}
	with open(songJsonPath, "r", encoding="utf-8") as songJson:
		songDict = json.load(songJson)
	songID = songDict["title"][1]
	if (not songID in masterSongDict):
		masterSongDict[songID] = []
	if (not bool(songDict)):
		print("\n\nAPPENDING AN EMPTY DICT FOR %s\n\n" % songID)
	masterSongDict[songID].append(songDict)
	if (len(masterSongDict[songID]) > 1):
		duplicateCount += 1
		if (not songID in duplicateIDList):
			duplicateIDList.append(songID)

# Iterate through each of the duplicates in masterSongDict
print("\nMerging all of the duplicate records...\n")
for duplicateSongID in duplicateIDList:
	merged = mergeDuplicates(masterSongDict[duplicateSongID])
	if (not bool(merged)):
		print("\n\nAPPENDING AN EMPTY DICT FOR %s\n\n" % duplicateSongID)
	masterSongDict[duplicateSongID] = merged

# Iterate through ALL songs in the masterSongDict
print("\nRe-iterating back over the songs to output the final json\n")
outputDict = {"songs": []}
for songID in masterSongDict.keys():
	songDict = {"blank": True}
	if (isinstance(masterSongDict[songID], list)):
		if (len(masterSongDict[songID]) > 1):
			print("\nSOMETHING IS WRONG. THERE'S A SONGDICT WITH BIG LENGTH FOR %s\n" % songID)
			continue
		songDict = masterSongDict[songID][0]
	else:
		songDict = masterSongDict[songID]
	if (isinstance(songDict["billboard_uid"], str)):
		if (songDict["billboard_uid"] == "<NONE>"):
			songDict["billboard_uid"] = []
		else:
			songDict["billboard_uid"] = [songDict["billboard_uid"]]
	if (isinstance(songDict["msd_uid"], str)):
		if (songDict["msd_uid"] == "<NONE>"):
			songDict["msd_uid"] = []
		else:
			songDict["msd_uid"] = [songDict["msd_uid"]]
	outputDict["songs"].append(songDict)

# Save the masterSongDict as one .json
with open("result.json", "w", encoding="utf-8") as outputJson:
	json.dump(outputDict, outputJson)
