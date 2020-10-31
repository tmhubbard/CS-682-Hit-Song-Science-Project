
# This script was written by Trevor Hubbard; its purpose is to validate
# the integrity of the data I downloaded from Genius

# =========================
#        * SETUP *
# =========================

# Some import statements
import textdistance, json, time, random, re
import pandas as pd
from pathlib import Path

# Some parameters for the validation
SONG_AMT = 1000
ALL_SONGS = False

# Parsing the msd CSV to prepare for DF creation
msdCSVPath = Path("C:\\Data\\College\\CS 682 - Neural Networks\\Project\\GitHub\\CS-682-Hit-Song-Science-Project\\Task 1\\Data\\msd - songs from 1990-2000.xlsx")
msdDict = {}
curTime = time.time()
print("\nWe're reading in the MSD .csv...")
msdDF = pd.read_excel(msdCSVPath)
headerList = (list(msdDF.columns))
print("It took %.2f sec to create a DataFrame from the MSD .csv!\n" % (time.time()-curTime))

# Create the msdDF from the parsed CSV info


# =========================
#       * METHODS *
# =========================

# This method will output the normalized Levenshtein similarity
# between word1 and word2
def stringSim(word1, word2):
	return textdistance.levenshtein.normalized_similarity(word1, word2)

# This method will convert a JSON object to a formatted string
def jprint(jsonObject):
	print((json.dumps(jsonObject, sort_keys = True, indent = 4)))

# This method will print the different titles and artists given in the Genius
# and MSD dataset for a given songID
def printSongInfo(songID):

	# Open the JSON corresponding with the songID
	songJSONPath = "C:\\Data\\Personal Study\\Datasets\\MSD - Genius Info (1990-2000)\\" + songID + ".json"
	with open(songJSONPath, "r", encoding="utf-8") as songJSON:
		
		# Grabbing relevant info (titles and artists) from the songJSON and the msdDF
		songJSONData = json.load(songJSON)
		songJSON_title = songJSONData["title"]
		songJSON_artist = songJSONData["primary_artist"]["name"]
		msdSeries = (msdDF.loc[msdDF['song_id'] == songID]).iloc[0]
		songDF_title = (msdSeries[headerList[0]])
		songDF_artist = ((msdSeries[headerList[1]]))

		# Transforming the title and artists to lowercase
		songJSON_artist = songJSON_artist.lower()
		songDF_artist = songDF_artist.lower()
		songJSON_title = songJSON_title.lower()
		songDF_title = songDF_title.lower()

		# Check if the MSD title has parentheses in it
		titleParens = re.search('\(.*\)', songDF_title)
		songDF_title_noParens = songDF_title
		if (titleParens):
			if (titleParens.span()[0] == 0): pass
			else:
				songDF_title_noParens = songDF_title[:titleParens.span()[0]]

		# Computing some stats about the string similarity of these
		artistSim = stringSim(songJSON_artist, songDF_artist)
		titleSim = stringSim(songJSON_title, songDF_title)
		titleSim_noParens = titleSim
		if (titleParens):
			titleSim_noParens = stringSim(songJSON_title, songDF_title_noParens)

		print("%s\n==================" % songID)
		print("Genius artist: %s" % songJSON_artist)
		print("MSD artist: %s" % songDF_artist)
		print("artist sim: %.3f\n" % artistSim)
		print("Genius title: %s" % songJSON_title)
		print("MSD title: %s" % songDF_title)
		print("title sim: %.3f" % titleSim)
		print("title sim WITHOUT parentheses: %.3f\n\n" % stringSim(songJSON_title, songDF_title_noParens))

# This method takes in a dict and an output file (the open file itself, not the 
# path) and will write each of the (key, value) pairs row-by-row 
def writeDictToFile(inputDict, outputFile):
	for key in inputDict.keys():
		strToWrite = key + ": " + str(inputDict[key]) + "\n"
		outputFile.write(strToWrite)

# =========================
#        * MAIN * 
# =========================

# Run through each of the songs in the MSD and check their information
# against the info in the Genius JSON
songDict = {}
found = False
for curSongNum, row in msdDF.iterrows():

	# Print some information about the progress of the process
	if (curSongNum % 1000 == 0):
		print("We've completed song %d / %d" % (curSongNum, len(msdDF)))
		outputFileName = "..\\Data\\outputFiles\\90s\\" + str(int(100 * curSongNum/len(msdDF))) + ".txt"
		outputFile = open(outputFileName, "w")
		writeDictToFile(songDict, outputFile)
		outputFile.close()

	# Load the JSON for the curSongID
	curSongID = row["song_id"]
	if (not found and curSongID != "SOFZIKW12A6D4F89C2"):
		continue
	else:
		found = True
	songJSONPath = Path("C:\\Data\\Personal Study\\Datasets\\MSD - Genius Info (1990-2000)\\" + curSongID + ".json")
	if (not songJSONPath.is_file()):
		songDict[curSongID] = -1
		continue
	with open(songJSONPath, "r", encoding="utf-8") as songJSON:

		# Grabbing relevant info (titles and artists) from the songJSON and the msdDF
		songJSONData = json.load(songJSON)
		songJSON_title = str(songJSONData["title"])
		if (songJSON_title == "<NONE>"):
			songDict[curSongID] = -1
			continue
		songJSON_artist = str(songJSONData["primary_artist"]["name"])
		msdSeries = (msdDF.loc[msdDF['song_id'] == curSongID]).iloc[0]
		songDF_title = str(msdSeries[headerList[0]])
		songDF_artist = str((msdSeries[headerList[1]]))

		# Transforming the title and artists to lowercase
		songJSON_artist = songJSON_artist.lower()
		songDF_artist = songDF_artist.lower()
		songJSON_title = songJSON_title.lower()
		songDF_title = songDF_title.lower()

		# Check if the MSD title has parentheses in it
		titleParens = re.search('\(.*\)', songDF_title)
		songDF_title_noParens = songDF_title
		if (titleParens):
			if (titleParens.span()[0] == 0): pass
			else:
				songDF_title_noParens = songDF_title[:titleParens.span()[0]]

		# Computing some stats about the string similarity of these
		artistSim = stringSim(songJSON_artist, songDF_artist)
		titleSim = stringSim(songJSON_title, songDF_title)
		titleSim_noParens = titleSim
		if (titleParens):
			titleSim_noParens = stringSim(songJSON_title, songDF_title_noParens)

		# If we've got artistSim > 0.8, we've most likely got the same artist
		if (artistSim > 0.7):
			# If the titleSim is lower than 0.8, check again without parentheses
			if (titleSim < 0.75):
				# If we're less than 0.6 similar in title, then add to badMatches
				if (titleSim_noParens <= 0.6):
					songDict[curSongID] = 0
					continue

				else:
					songDict[curSongID] = 1

			else: 
				songDict[curSongID] = 1


		# If we've got 0.5 <= artistSim <= 0.8, then we *might* have the same artist; 
		# I've got to look at the titleSim to better determine this 
		elif (artistSim >= 0.4):
			if (titleSim < 0.75):
				if (titleSim_noParens <= 0.6):
					songDict[curSongID] = 0
					continue
				else:
					songDict[curSongID] = 1
			else:
				songDict[curSongID] = 1

		# Otherwise, check if the title similarity without parentheses is above 0.8
		elif(titleSim_noParens > 0.8):

			# If it is, but the artist similarity is below 0.3, then add to badMatches
			if (artistSim < 0.3):
				songDict[curSongID] = 0
				continue

			else:
				songDict[curSongID] = 1

		# If all else fails, append this to badMatches
		else:
			songDict[curSongID] = 0
			continue

outputFile = open("final output.txt", "w")
writeDictToFile(songDict, outputFile)
outputFile.close()
