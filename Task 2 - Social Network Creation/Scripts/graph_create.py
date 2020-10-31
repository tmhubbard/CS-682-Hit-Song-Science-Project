
# This script was written by Trevor Hubbard; its purpose is to create a graph
# from the various artists in the Genius dataset

# =========================
#        * SETUP *
# =========================

# Import statements
import json
import pandas as pd
import networkx as nx
import ast

# Parameter to do "more connections graph"
MORE_CONNECTIONS = True
MORE_CONNECTIONS_SMART = True

# =========================
#       * METHODS *
# =========================


# =========================
#        * MAIN * 
# =========================

# Create the graph
graph = nx.DiGraph()
if(MORE_CONNECTIONS): graph = nx.Graph()
songName = {}

# Open the dataset
artistDict = {}
with open("../Data/Genius Info - Billboard + MSD, 1990-2010.json", "r", encoding="utf-8") as datasetJson:
	songList = json.load(datasetJson)["songs"]
	for songNum, songDict in enumerate(songList):

		print("Reading in song %d..." % songNum)

		artistName, artistID, artistTypes = songDict["artist"]
		if (not artistID in artistDict):
			artistDict[artistID] = {"name": artistName, "ID": artistID, "songs": [], "collaborators": [], "types": []}

		# Add song
		songID = songDict["title"][1]
		songName[songID] = songDict["title"][0]
		artistDict[artistID]["songs"].append(songID)

		# Add collaborators
		for collaborator in songDict["collaborators"]:
			collaboratorName, collaboratorID, collaboratorTypes = collaborator
			if (not collaboratorID in artistDict):
				artistDict[collaboratorID] = {"name": collaboratorName, "ID": collaboratorID, "songs": [], "collaborators": [], "types": []}

			# Add song 
			artistDict[collaboratorID]["songs"].append(songID)

			# If MORE_CONNECTIONS_SMART is on, make edges between all of the collaborators 
			if (MORE_CONNECTIONS_SMART):

				# Connect all of the collaborators with eachother as co-collaborators
				for otherColab in songDict["collaborators"]:

					# Collect info
					otherColabName, otherColabID, otherColabTypes = otherColab

					# Skip it if it's a self loop
					if (otherColabID==collaboratorID): continue

					# Make the node if it hasn't been there yet
					if (not otherColabID in artistDict):
						artistDict[otherColabID] = {"name": otherColabName, "ID": otherColabID, "songs": [], "collaborators": [], "types": []}

					# Add this otherColab ID to the artist
					artistDict[collaboratorID]["collaborators"].append((otherColabID, songID))

			# Add types
			for collaboratorType in collaboratorTypes:
				artistDict[collaboratorID]["types"].append((collaboratorType, songID))

			# Add this collaborator ID to the artist
			artistDict[artistID]["collaborators"].append((collaboratorID, songID))

		# Add types
		for artistType in artistTypes:
			artistDict[artistID]["types"].append((artistType, songID))

# Adding the MaxType attribute to each author
for artistID in artistDict.keys():
	typeList = artistDict[artistID]["types"]
	typeDict = {}
	for curType in typeList:
		curType = curType[0]
		if (not curType in typeDict):
			typeDict[curType] = 0
		typeDict[curType] += 1
	sortedTypes = {k: v for k, v in sorted(typeDict.items(), key=lambda item: item[1], reverse=True)}
	artistDict[artistID]["maxType"] = list(sortedTypes.keys())[0]

# Creating nodes for each artist in the dict
numArtists = len(list(artistDict.keys()))
for artistNum, artistID in enumerate(list(artistDict.keys())):

	# Declare variables for the current artist
	curArtistDict = artistDict[artistID]
	artistName = curArtistDict["name"]
	collaboratorList = curArtistDict["collaborators"]
	typeList = curArtistDict["types"]
	maxType = curArtistDict["maxType"]

	print("%d / %d: Adding %s to the graph..." % (artistNum, numArtists, artistName))

	# Add the node for the current artist
	graph.add_node(artistID, name=artistName, types=str(typeList), maxType=maxType)

	# Add edges between the artist and all of the other collaborators
	for collaborator in collaboratorList:

		# If the collaborator isn't in the graph, create a node for them
		collaboratorID, songID = collaborator
		curRelationship = "<NONE>"
		collaboratorName = artistDict[collaboratorID]["name"]
		collaboratorTypes = artistDict[collaboratorID]["types"]
		collaboratorMaxType = artistDict[collaboratorID]["maxType"]
		if (not graph.has_node(collaboratorID)):
			graph.add_node(collaboratorID, name=collaboratorName, types=str(collaboratorTypes), maxType=collaboratorMaxType)

		foundRelationship = False
		for curType, curSong in collaboratorTypes:
			if (not foundRelationship and curSong == songID):
				curRelationship = curType
				foundRelationship = True

		# The MORE_CONNECTIONS flag will make:
		#    1) The graph edges undirected
		#	 2) All of the collaborators connected
		if (MORE_CONNECTIONS):

			# This is wildly inefficient and bad and wasn't a great idea
			if (not MORE_CONNECTIONS_SMART):
				# Add an edge between this collaborator and every other collaborator
				for otherColab in collaboratorList:

					# If the collaborator isn't in the graph, create a node for them
					otherColabID, songID = otherColab

					# Skip this if we've done it before
					if (otherColabID == collaboratorID):
						continue

					coCollab = "Co-collaborator"
					otherColabName = artistDict[otherColabID]["name"]
					otherColabTypes = artistDict[otherColabID]["types"]
					otherColabMaxType = artistDict[otherColabID]["maxType"]
					if (not graph.has_node(otherColabID)):
						graph.add_node(otherColabID, name=otherColabName, types=str(otherColabTypes), maxType=otherColabMaxType)

					# If the graph already has an edge between (collaborator, otherColab),
					# then snag their lists and set them to the respective variables
					songIDList = []
					songNameList = []
					relationshipList = []
					if (graph.has_edge(collaboratorID, otherColabID)):
						edgeData = graph.get_edge_data(collaboratorID, otherColabID)
						songIDList = ast.literal_eval(edgeData["songID"])
						songList = ast.literal_eval(edgeData["song"])
						relationshipList = ast.literal_eval(edgeData["relationship"])

					# Add this collaboration's information to the graph
					songIDList.append(songID)
					songNameList.append(songName[songID])
					relationshipList.append(coCollab)

					# Add the edge to the dict
					graph.add_edge(collaboratorID, otherColabID, songID=str(songIDList), song=str(songNameList), relationship=str(relationshipList))

			# Now, add an edge between the collaborator and the primary artist.
			# Since we're doing an undirected graph w/ MORE_CONNECTIONS, though,
			# we'll have to append some of this list data to the lists 
			songIDList = []
			songNameList = []
			relationshipList = []
			if (graph.has_edge(collaboratorID, otherColabID)):
				edgeData = graph.get_edge_data(collaboratorID, otherColabID)
				songIDList = ast.literal_eval(edgeData["songID"])
				songList = ast.literal_eval(edgeData["song"])
				relationshipList = ast.literal_eval(edgeData["relationship"])

			# Add this collaboration's information to the graph
			songIDList.append(songID)
			songNameList.append(songName[songID])
			relationshipList.append(curRelationship)

			# Add the edge to the dict
			graph.add_edge(collaboratorID, artistID, songID=str(songIDList), song=str(songNameList), relationship=str(relationshipList))
			
		# If this isn't MORE_CONNECTIONS... just add the edge between
		# the collaborator and the primary_artist! 
		else:
			# Make an edge between this node and the artist
			graph.add_edge(collaboratorID, artistID, songID=songID, song=songName[songID], relationship=curRelationship)

nx.write_graphml(graph, "outputGraph.graphml")

