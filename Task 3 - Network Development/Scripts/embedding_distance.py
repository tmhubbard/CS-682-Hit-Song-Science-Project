
# This script was written by Trevor Hubbard; its purpose is two quickly calculate 
# this distance between some points in a network embedding

# =========================
#        * SETUP *
# =========================

import numpy as np
import pandas as pd

# =========================
#       * CLASSES *
# =========================


# =========================
#       * METHODS *
# =========================

def nodeDistance(node1, node2):
	node1 = np.array(node1[1])
	node2 = np.array(node2[1])
	return np.linalg.norm(node1-node2)

# =========================
#        * MAIN * 
# =========================

# Load the embedding
nodes = []
lineNum = 0
with open("../Data/industryGraph - 128 dim embedding.emd", "r", encoding="utf-8") as embeddingFile:
	for line in embeddingFile:
		lineNum += 1
		if (lineNum == 1): continue
		if (lineNum > 1000):
			break
		splitLine = [float(x) for x in line.split()]
		nodeID = int(splitLine[0])
		embedding = splitLine[1:]
		nodes.append((nodeID, embedding))

distanceDict = {} 
for firstNode in nodes:
	for otherNode in nodes: 
		if (firstNode[0] == otherNode[0]): continue
		edgeID = str(firstNode[0]) + " - " + str(otherNode[0])
		alternativeEdgeID = str(otherNode[0]) + " - " + str(firstNode[0])
		if (alternativeEdgeID in distanceDict): 
			distanceDict[edgeID] = distanceDict[alternativeEdgeID]
		elif (edgeID in distanceDict):
			distanceDict[alternativeEdgeID] = distanceDict[edgeID]
		else:
			curDistance = nodeDistance(firstNode, otherNode)
			distanceDict[alternativeEdgeID] = curDistance
			distanceDict[edgeID] = curDistance

distanceDict = {k: v for k, v in sorted(distanceDict.items(), key=lambda item: item[1])}


distanceDF = pd.DataFrame(distanceDict, index=["distance"]).transpose()
distanceDF.to_excel("final.xlsx")