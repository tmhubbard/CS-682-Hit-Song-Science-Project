
# This script was written by Trevor Hubbard; its purpose is to preprocess the song
# embedding data by normalizing each dimension in the data

# =========================
#        * SETUP *
# =========================

import pandas as pd
import numpy as np

good = 34
minVal = 0
maxVal = 1

# =========================
#       * CLASSES *
# =========================


# =========================
#       * METHODS *
# =========================

def minMaxNormalize(x):
	if (x != -10.0):
		newVal = (x-minVal)/(maxVal-minVal)
		return newVal
	else:
		return -.1

# =========================
#        * MAIN * 
# =========================

print("\nReading in the .xlsx file containing the data...")
datasetPath = "C:\Data\College\CS 682 - Neural Networks\Project\Task 3 - Network Development\Data\Song Embeddings - Average.xlsx"
datasetDF = pd.read_excel(datasetPath)
print("Finished reading in the data!")

print("\nNormalizing the data...")
for embDim in [("emb_dim_%d" % dimNum) for dimNum in range(10)]:
	newStuff = np.array(datasetDF[embDim])
	minVal = (min(x for x in newStuff if x != -10.0))
	maxVal = (max(x for x in newStuff))
	datasetDF[embDim] = datasetDF[embDim].apply(minMaxNormalize)
print("Finished normalizing the data!")

print("\nSaving the data...")
datasetDF.to_excel("../Data/Song Embeddings - Average, Normalized.xlsx")
print("Finished saving the data!")