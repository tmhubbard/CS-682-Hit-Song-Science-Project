
# This script was written by Trevor Hubbard; its purpose is to clean the dataset
# by scraping it of any irelevant information / bucketing the artists

# =========================
#        * SETUP *
# =========================

# Some import statements
import json
from pathlib import Path
from shutil import copyfile

# Create the list of performer types from the .tsv
performerTypesPath = Path("C:\Data\College\CS 682 - Neural Networks\Project\GitHub\CS-682-Hit-Song-Science-Project\Task 2\Data\PerformanceLabels-GROUPED.tsv")
performerTypesDict = {}
with open(performerTypesPath, "r") as performerTypesTSV:
	for line in performerTypesTSV:
		splitLine = [x.strip() for x in line.split("\t")]
		for label in splitLine:
			performerTypesDict[label] = splitLine[0]

# Ask the user for a couple of paths
inputPath = Path(input("Please enter the path of the folder containing .json's you want to clean: "))
outputPath = Path(input("Please enter the path of the folder where you want to output cleaned .json's: "))

# =========================
#        * METHODS *
# =========================

# This method will return the "performer type" for a given performer 
def getPerformerType(performerLabel):
	if (performerLabel in performerTypesDict):
		return performerTypesDict[performerLabel]
	else:
		return "Misc."

# This method will "clean" a songDict by scraping it of any irelevant information, 
# and bucketing artists into particular groups
def cleanSongDict(jsonPath):

	# Opening the given json 
	with open(jsonPath, "r") as songJSON:

		# Setting up the parsing
		jsonName = jsonPath.stem
		songDict = json.load(songJSON)

		# Creating the song dict that we'll populate using the info from songDict
		newSongDict = {"title": (),
					   "artist": (),
					   "collaborators": [],
					   "year": "<NONE>",
					   "hit": False,
					   "billboard_uid": "<NONE>",
					   "msd_uid": "<NONE>"}

		# Populate newSongDict with the song name and primary artist
		newSongDict["title"] = (songDict["title"], songDict["id"])
		newSongDict["artist"] = (songDict["primary_artist"]["name"], songDict["primary_artist"]["id"], ["Primary Artist"])

		# Add in the information about any of the collaborators in custom_performances
		if ("custom_performances" in songDict):
			for collaboratorDict in songDict["custom_performances"]:
				collaboratorType = getPerformerType(collaboratorDict["label"])
				for collaborator in collaboratorDict["artists"]:
					curCollaborator = (collaborator["name"], collaborator["id"], [collaboratorType])
					newSongDict["collaborators"].append(curCollaborator)

		# Add in the information about the producers
		if ("producer_artists" in songDict):
			for producerDict in songDict["producer_artists"]:
				curProducer = (producerDict["name"], producerDict["id"], ["Producer"])
				newSongDict["collaborators"].append(curProducer)

		# Add in the information about the writers
		if ("writer_artists" in songDict):
			for writerDict in songDict["writer_artists"]:
				curWriter = (writerDict["name"], writerDict["id"], ["Writer"])
				newSongDict["collaborators"].append(curWriter)

		# Add in the information about the featured artists
		if ("featured_artists" in songDict):
			for featureDict in songDict["featured_artists"]:
				curFeature = (featureDict["name"], featureDict["id"], ["Featured Artist"])
				newSongDict["collaborators"].append(curFeature)

		# Check if the song is a hit by looking at the filename of the .json
		# (B's are from the Billboard charts, S is from the MSD)
		if (jsonName.startswith("B")):
			newSongDict["hit"] = True
			newSongDict["billboard_uid"] = jsonName

		# If it's not, just add the MSD UID to the new dict
		elif (jsonName.startswith("S")):
			newSongDict["msd_uid"] = jsonName

		# Deduplicate the collaborator list
		curCollaboratorList = newSongDict["collaborators"]
		curCollaboratorDict = {}
		for collaborator in curCollaboratorList:

			# If the primary artist is listed as a collaborator, then append
			# their collaborator type to the primary artist and continue
			if (collaborator[1] == newSongDict["artist"][1]):
				for label in collaborator[2]:
					if (not label in newSongDict["artist"][2]):
						newSongDict["artist"][2].append(label)
				continue

			# Add the collaborator's labels to the curCollaboratorDict
			if (not collaborator[1] in curCollaboratorDict):
				curCollaboratorDict[collaborator[1]] = (collaborator[0], collaborator[1], [])
			for label in collaborator[2]:
				if (not label in curCollaboratorDict[collaborator[1]][2]):
					curCollaboratorDict[collaborator[1]][2].append(label)

		newCollaboratorList = []
		for key in curCollaboratorDict.keys():
			newCollaboratorList.append(curCollaboratorDict[key])
		newSongDict["collaborators"] = newCollaboratorList

		# Return the cleaned song ID
		return newSongDict

# =========================
#        * MAIN * 
# =========================

# Iterate through each of the .json's in inputPath
curChildFile = 0
for childJson in inputPath.iterdir():
	curChildFile += 1
	print("%d: %s" % (curChildFile, childJson.stem))
	outputFileName = outputPath / Path(childJson.stem + ".json")
	if (outputFileName.is_file()):
		continue
	with open(outputFileName, "w", encoding="utf-8") as outputJson:
		json.dump(cleanSongDict(childJson), outputJson)
