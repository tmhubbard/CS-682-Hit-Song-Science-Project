
# This script was written by Trevor Hubbard; its purpose is to create a graph
# from the various artists in the Genius dataset

# =========================
#        * SETUP *
# =========================

# Import statements
import json, datetime, ast
import lxml.etree as ET
import pandas as pd
import networkx as nx

# Parameter to do "more connections graph"
MORE_CONNECTIONS = True
MORE_CONNECTIONS_SMART = True

# If this is true, it'll only create the graph out of the first 100
# songs. (This is meant to test if things are working)
EARLY_STOP = False

# Some parameters for the gexf stuff
nodesDict = {}
edgesDict = {}
nodeStartDict = {}
nodeEndDict = {}
edgeStartDict = {}
edgeEndDict = {}
songYearDict = {}
expirationDate = 1

# =========================
#       * METHODS *
# =========================

# This method will create a node in the graph 
def createGexfNode(gexfNodesElement, nodeTuple):
	nodeID, nodeData = nodeTuple
	startDate, endDate = findNodeLifespan(nodeTuple)
	nodesDict[nodeID] = ET.SubElement(gexfNodesElement, "node", id=str(nodeID), label=str(nodeID), start=startDate, end=endDate)
	nodeAttElement = ET.SubElement(nodesDict[nodeID], "attvalues")
	nodeAttDict = {}
	nodeDataList = list(nodeData.keys())
	for attNum, key in enumerate(nodeDataList):
		attValue = nodeData[key]
		nodeAttDict[key] = ET.SubElement(nodeAttElement, "attvalue", {"for": str(attNum), "value": str(attValue)})

# This method will create an edge in the graph 
def createGexfEdge(gexfEdgesElement, edgeTuple):
	sourceNode, targetNode, edgeDataDict = edgeTuple
	startDate, endDate = findEdgeLifespan(edgeTuple)
	songID = edgeDataDict["songID"]
	edgeWeight = str(len(((ast.literal_eval(edgeDataDict["relationship"])))))
	edgeID = str(sourceNode) + " - " + str(targetNode) + " - " + str(songID)
	edgesDict[edgeID] = ET.SubElement(gexfEdgesElement, "edge", id=str(edgeID), label=str(edgeID), source=str(sourceNode), target=str(targetNode), start=startDate, end=endDate, weight=edgeWeight)
	edgeAttElement = ET.SubElement(edgesDict[edgeID], "attvalues")
	edgeAttDict = {}
	edgeDataList = list(edgeDataDict.keys())
	for attNum, key in enumerate(edgeDataList):
		attValue = edgeDataDict[key]
		# print(key)
		# print(attValue)
		edgeAttDict[key] = ET.SubElement(edgeAttElement, "attvalue", {"for": str(attNum), "value": str(attValue)})

# This method will return a tuple of (start year, end year) when
# given a nodeTuple
def findNodeLifespan(nodeTuple):
	nodeID, nodeData = nodeTuple
	typeList = ast.literal_eval(nodeData["types"])
	firstYear = None
	lastYear = None
	for curType, curSongID in typeList:
		curYear = songYearDict[curSongID]
		if (firstYear is None):
			firstYear = curYear
		if (lastYear is None):
			lastYear = curYear
		if (curYear < firstYear):
			firstYear = curYear
		if (curYear > lastYear):
			lastYear = curYear
	firstYearString = str(firstYear) + "-01-01"
	lastYearString = str(int(lastYear) + (expirationDate)) + "-01-01"
	return (firstYearString, lastYearString)

# This method will return a tuple of (start year, end year) when
# given an edgeTuple
def findEdgeLifespan(edgeTuple):
	sourceNode, targetNode, edgeData = edgeTuple
	edgeYear = ast.literal_eval(edgeData["year"])
	firstYear = None
	lastYear = None

	# If we're dealing w/ an undirected graph
	if (isinstance(edgeYear, list)):
		for curYear in edgeYear:
			if (firstYear is None):
				firstYear = curYear
			if (lastYear is None):
				lastYear = curYear
			if (curYear < firstYear):
				firstYear = curYear
			if (curYear > lastYear):
				lastYear = curYear

	# Otherwise, if we're dealing w/ a directed graph
	else:
		firstYear = edgeYear
		lastYear = edgeYear

	firstYearString = str(firstYear) + "-01-01"
	lastYearString = str(int(lastYear) + expirationDate) + "-01-01"
	return (firstYearString, lastYearString)

# =========================
#        * MAIN * 
# =========================

# Ask the user if they want to create an undirected / directed graph
userInput = input("\nWhich type of graph do you want to create?\n\n\t1) Undirected Graph\n\t2) Directed Graph\n\nType either number as your choice, and hit ENTER: ")
if (userInput == "1"):
	MORE_CONNECTIONS = True
	MORE_CONNECTIONS_SMART = True
elif (userInput == "2"):
	MORE_CONNECTIONS = False
	MORE_CONNECTIONS_SMART = False

# 1) Load your data for the gexf

# Create the graph
graph = nx.DiGraph()
if(MORE_CONNECTIONS): graph = nx.Graph()
songName = {}
songYear = {}

# Open the dataset
artistDict = {}
with open("../Data/Genius Info - Billboard + MSD, 1990-2010.json", "r", encoding="utf-8") as datasetJson:
	songList = json.load(datasetJson)["songs"]
	for songNum, songDict in enumerate(songList):

		if (EARLY_STOP and songNum == 100):
			break

		print("Reading in song %d..." % (songNum))

		artistName, artistID, artistTypes = songDict["artist"]
		artistID = str(artistID) + " (" + artistName + ")"
		if (not artistID in artistDict):
			artistDict[artistID] = {"name": artistName, "ID": artistID, "songs": [], "collaborators": [], "types": []}

		# Add song
		songID = songDict["title"][1]
		songYear[songID] = songDict["year"]
		songName[songID] = songDict["title"][0]
		artistDict[artistID]["songs"].append(songID)

		# Add the song, year combo to the songYearDict
		songYearDict[songID] = songDict["year"]

		# Add collaborators
		for collaborator in songDict["collaborators"]:
			collaboratorName, collaboratorID, collaboratorTypes = collaborator
			collaboratorID = str(collaboratorID) + " (" + collaboratorName + ")"
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
					otherColabID = str(otherColabID) + " (" + otherColabName + ")"

					# Skip it if it's a self loop
					if (otherColabID==collaboratorID): continue

					# Make the node if it hasn't been there yet
					if (not otherColabID in artistDict):
						artistDict[otherColabID] = {"name": otherColabName, "ID": otherColabID, "songs": [], "collaborators": [], "types": []}

					# Add this otherColab ID to the artist
					artistDict[collaboratorID]["collaborators"].append((otherColabID, songID, True))

			# Add types
			for collaboratorType in collaboratorTypes:
				artistDict[collaboratorID]["types"].append((collaboratorType, songID))

			# Add this collaborator ID to the artist
			artistDict[artistID]["collaborators"].append((collaboratorID, songID, False))

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

	print("\n%d / %d: Adding %s to the graph..." % (artistNum, numArtists, artistName))

	# Add the node for the current artist
	graph.add_node(artistID, name=artistName, types=str(typeList), maxType=maxType)

	# Add edges between the artist and all of the other collaborators
	for collaborator in collaboratorList:

		# If the collaborator isn't in the graph, create a node for them
		collaboratorID, songID, coColab = collaborator
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
					yearList = []
					songNameList = []
					relationshipList = []
					if (graph.has_edge(collaboratorID, otherColabID)):
						edgeData = graph.get_edge_data(collaboratorID, otherColabID)
						songIDList = ast.literal_eval(edgeData["songID"])
						songList = ast.literal_eval(edgeData["song"])
						yearList = ast.literal_eval(edgeData["year"])
						relationshipList = ast.literal_eval(edgeData["relationship"])

					# Add this collaboration's information to the graph
					if (not songID in songIDList):
						songIDList.append(songID)
						songNameList.append(songName[songID])
						yearList.append(songYear[songID])
						relationshipList.append(coCollab)

					# Add the edge to the dict
					graph.add_edge(collaboratorID, otherColabID, songID=str(songIDList), song=str(songNameList), year = str(yearList), relationship=str(relationshipList))

			# If coColab is set to true, we'll change the relationship to "Co-collaborator"
			colabRelationship = curRelationship
			if (coColab):
				colabRelationship = "Co-collaborator"

			# Now, add an edge between the collaborator and the primary artist.
			# Since we're doing an undirected graph w/ MORE_CONNECTIONS, though,
			# we'll have to append some of this list data to the lists 
			songIDList = []
			songNameList = []
			yearList = []
			relationshipList = []
			if (graph.has_edge(artistID, collaboratorID)):
				edgeData = graph.get_edge_data(artistID, collaboratorID)
				songIDList = ast.literal_eval(edgeData["songID"])
				songNameList = ast.literal_eval(edgeData["song"])
				yearList = ast.literal_eval(edgeData["year"])
				relationshipList = ast.literal_eval(edgeData["relationship"])

			# Add this collaboration's information to the graph if it wasn't
			# there before
			if (not songID in songIDList):
				songIDList.append(songID)
				songNameList.append(songName[songID])
				yearList.append(songYear[songID])
				relationshipList.append(colabRelationship)

			# Add the edge to the dict
			graph.add_edge(collaboratorID, artistID, songID=str(songIDList), song=str(songNameList), year=str(yearList), relationship=str(relationshipList))
			
		# If this isn't MORE_CONNECTIONS... just add the edge between
		# the collaborator and the primary_artist! 
		else:

			# Now, add an edge between the collaborator and the primary artist.
			songIDList = []
			songNameList = []
			yearList = []
			relationshipList = []
			if (graph.has_edge(collaboratorID, artistID)):
				edgeData = graph.get_edge_data(collaboratorID, artistID)
				songIDList = ast.literal_eval(edgeData["songID"])
				songNameList = ast.literal_eval(edgeData["song"])
				yearList = ast.literal_eval(edgeData["year"])
				relationshipList = ast.literal_eval(edgeData["relationship"])

			# Add this collaboration's information to the graph if it wasn't
			# there before
			if (not songID in songIDList):
				songIDList.append(songID)
				songNameList.append(songName[songID])
				yearList.append(songYear[songID])
				relationshipList.append(curRelationship)


			# Make an edge between this node and the artist
			graph.add_edge(collaboratorID, artistID, songID=str(songIDList), song=str(songNameList), year=str(yearList), relationship=str(relationshipList))

# 2) Set up attribute sub-elements for each of the node and edge attributes

# Setting up the XML ElementTree 
defaultEdgeType = "directed"
if (MORE_CONNECTIONS):
	defaultEdgeType = "undirected"
attr_qname = ET.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
gexf = ET.Element('gexf', 
                 {attr_qname: 'http://www.gexf.net/1.3draft  http://www.gexf.net/1.3draft/gexf.xsd'}, 
                 nsmap={None: 'http://graphml.graphdrawing.org/xmlns/graphml'},
                 version='1.3')
graph_ET = ET.SubElement(gexf,'graph', defaultedgetype=defaultEdgeType, mode='dynamic', timeformat="date")
nodeAttributes = ET.SubElement(graph_ET, "attributes", {"class": "node"})
edgeAttributes = ET.SubElement(graph_ET, "attributes", {"class": "edge"})
nodes = ET.SubElement(graph_ET, "nodes")
edges = ET.SubElement(graph_ET, "edges")

# Setting up each of the node attributes
artistID, nodeDataDict = (list(graph.nodes(data=True))[0])
nodeDataList = list(nodeDataDict.keys())
for nodeDataID, nodeData in enumerate(nodeDataList):
	nodeAttribute = ET.SubElement(nodeAttributes, "attribute", id=str(nodeDataID), title=nodeData, type="string")

# Setting up each of the edge attributes
sourceNode, targetNode, edgeDataDict = (list(graph.edges(data=True))[0])
edgeDataList = list(edgeDataDict.keys())
for edgeDataID, edgeData in enumerate(edgeDataList):
	edgeAttribute = ET.SubElement(edgeAttributes, "attribute", id=str(edgeDataID), title=edgeData, type="string")

# 3) Create all of the nodes in your data 
for node in graph.nodes(data=True):
	createGexfNode(nodes, node)

# 4) Create edges between the authors
for edge in graph.edges(data=True):
	createGexfEdge(edges, edge)

# 5) Write the ElementTree to a .gexf file
outputName = "Dynamic "
if (MORE_CONNECTIONS):
	outputName = outputName + "Undirected Network.gexf"
else:
	outputName = outputName + "Directed Network.gexf"
tree = ET.ElementTree(gexf)
tree.write(outputName)
