
# This script was written by Trevor Hubbard; its purpose is two quickly calculate 
# this distance between some points in a network embedding

# =========================
#        * SETUP *
# =========================

import matplotlib.pyplot as plt

# =========================
#       * CLASSES *
# =========================


# =========================
#       * METHODS *
# =========================


# =========================
#        * MAIN * 
# =========================

# This creates the class from the node embeddings
ballPoints = []
boomerangPoints = []
embeddingPath = "C:\Data\College\CS 682 - Neural Networks\Project\Task 3 - Network Development\Data\industryGraph - 2 dim embedding.emd"
with open(embeddingPath, "r", encoding="utf-8") as embeddingFile:

	for embeddingNum, embedding in enumerate(embeddingFile):
		if (embeddingNum == 0): continue #Skip the first line
		nodeID, xVal, yVal = [float(x) for x in embedding.split()]
		nodeID = int(nodeID)
		if (xVal < -2 and yVal < -1): 
			ballPoints.append((xVal, yVal))
		else:
			boomerangPoints.append((xVal, yVal))

ballPointsX = [x[0] for x in ballPoints]
ballPointsY = [x[1] for x in ballPoints]
boomerangPointsX = [x[0] for x in boomerangPoints]
boomerangPointsY = [x[1] for x in boomerangPoints]
plt.scatter(ballPointsX, ballPointsY, color="green")
plt.scatter(boomerangPointsX, boomerangPointsY, color="purple")
plt.show()