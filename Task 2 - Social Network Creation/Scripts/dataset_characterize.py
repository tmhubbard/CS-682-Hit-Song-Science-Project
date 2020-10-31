
# This script was written by Trevor Hubbard; its purpose is to create an
# xlsx file characterizing all of the data in the Genius dataset; this is
# for the purpose of exploratory work before creating the social network

# =========================
#        * SETUP *
# =========================

import json
import pandas as pd


# =========================
#       * CLASSES *
# =========================


# =========================
#       * METHODS *
# =========================


# =========================
#        * MAIN * 
# =========================

# Open the dataset
artistDict = {}
with open("../Data/Genius Info - Billboard + MSD, 1990-2010.json", "r", encoding="utf-8") as datasetJson:
	songList = json.load(datasetJson)["songs"]
	for songNum, songDict in enumerate(songList):

		print("Adding %d to the artistDict..." % songNum)
		if (len(artistDict) > 1000000):
			break

		artistName, artistID, artistTypes = songDict["artist"]
		if (not artistID in artistDict):
			artistDict[artistID] = {"name": artistName, "ID": artistID, "songs": [], "collaborators": [], "types": []}

		# Add song
		songID = songDict["title"][1]
		artistDict[artistID]["songs"].append(songID)

		# Add collaborators
		for collaborator in songDict["collaborators"]:
			collaboratorName, collaboratorID, collaboratorTypes = collaborator
			if (not collaboratorID in artistDict):
				artistDict[collaboratorID] = {"name": collaboratorName, "ID": collaboratorID, "songs": [], "collaborators": [], "types": []}

			# Add song 
			artistDict[collaboratorID]["songs"].append(songID)

			# Add types
			for collaboratorType in collaboratorTypes:
				if (not collaboratorType in artistDict[collaboratorID]["types"]):
					artistDict[collaboratorID]["types"].append(collaboratorType)

			# Add this collaborator ID to the artist
			artistDict[artistID]["collaborators"].append(collaboratorID)

		# Add types
		for artistType in artistTypes:
			if (not artistType in artistDict[artistID]["types"]):
				artistDict[artistID]["types"].append(artistType)

print("\nIterating over each artist in the artistDF and adding new attributes...")
for artistID in artistDict.keys():
	artistDict[artistID]["Collaborator Count"] = len(artistDict[artistID]["collaborators"])
	artistDict[artistID]["Song Count"] = len(artistDict[artistID]["songs"])

print("\nConverting the dict to a DataFrame...")
artistDF = pd.DataFrame.from_dict(artistDict)

print("\nSaving the DataFrame as an .xlsx file...")
artistDF.transpose().to_excel("characterized.xlsx", index=False)
