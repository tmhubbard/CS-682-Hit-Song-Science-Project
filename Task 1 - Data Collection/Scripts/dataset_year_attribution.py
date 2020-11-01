
# This script was written by Trevor Hubbard; its purpose is to attribute
# years to the songs in the cleaned Genius info .json

# =========================
#        * SETUP *
# =========================

# Import statements
import json
from pathlib import Path

# Setup the datasetDict 
datasetJsonPath = "C:\Data\College\CS 682 - Neural Networks\Project\Task 1 - Data Collection\Data\Genius Info - Billboard + MSD, 1990-2010.json"
datasetDict = {}
with open(datasetJsonPath, "r", encoding="utf-8") as datasetJson:
	datasetDict = json.load(datasetJson)

# Set up the dict of UIDs --> .json file paths
uidJsonDict = {}

# Iterate through each folder containing .json's 
billboardJsonFolder = Path("..\Data\Genius .json's\Validated Raw\Billboard - Genius Info (1990 - 2010) - VALIDATED")
msd1JsonFolder = Path("..\Data\Genius .json's\Validated Raw\MSD - Genius Info (1990-2000) - VALIDATED")
msd2JsonFolder = Path("..\Data\Genius .json's\Validated Raw\MSD - Genius Info (2000-2010) - VALIDATED")
folderList = [billboardJsonFolder, msd1JsonFolder, msd2JsonFolder]
for folder in folderList:

	# Iterate through each file in the folder
	for jsonFile in folder.iterdir():

		# Add the (uid, .json path) pair to the uidJsonDict
		uidJsonDict[jsonFile.stem] = jsonFile 

# =========================
#       * METHODS *
# =========================

# This method will locate the raw Genius .json for a given song when given
# either a Billboard or MSD UID
def findRawJson(uid):
	if (uid in uidJsonDict):
		return uidJsonDict[uid]
	else:
		return None

# This method will search a raw Genius .json for a release_date value, and
# return the year if it's found
def findReleaseYear(jsonPath):

	# Open the json, load it to a dict, and return the year (or None if 
	# the year isn't found)
	with open(jsonPath, "r", encoding="utf-8") as jsonFile:
		songDict = json.load(jsonFile)
		if ("release_date" in songDict):
			release = songDict["release_date"]
			if (not release is None):
				year = release.split("-")[0]
				return year
		return None

# This method will take in an open file and a dict, and write each key, value
# pair on a separate line of a csv
def dictToCsv(inputDict, openFile):

	# Iterate over each key in the inputDict and write it to openFile
	for dictKey in inputDict.keys():
		openFile.write("%s, %s\n" % (dictKey, inputDict[dictKey]))

# This method will extract all of the UID, year pairs from the Genius .json's
def extractYearInfo_geniusJsons():

	# Iterate over each song in the .json
	songAmt = len(datasetDict["songs"])
	uidYearDict = {}
	for songNum, songDict in enumerate(datasetDict["songs"]):

		# Print if we can't find the file 
		billboardUIDList = songDict["billboard_uid"]
		msdUIDList = songDict["msd_uid"]
		UIDs = billboardUIDList + msdUIDList

		# Iterate through each UID and check if there's a year in the .json file
		releaseYears = []
		for uid in UIDs:
			rawJsonPath = findRawJson(uid)

			# If there's a year, append it to the releaseYears
			if (not rawJsonPath is None):
				releaseYear = findReleaseYear(rawJsonPath)
				if (not releaseYear is None):
					releaseYears.append(releaseYear)

		# Adding the release year to the uidYearDict
		if (len(releaseYears) > 0):
			for uid in UIDs:
				uidYearDict[uid] = releaseYears[0]

		# Write the list of (uid, year) pairs to disk every 5,000 songs
		if ((songNum % 5000) == 0):
			print("Saving the years of the first %d songs..." % songNum)
			with open("../Data/UID-Year mappings - genius info.csv", "w", encoding="utf-8") as outputFile:
				dictToCsv(uidYearDict, outputFile)
	
	with open("../Data/UID-Year mappings - genius info.csv", "w", encoding="utf-8") as outputFile:
		dictToCsv(uidYearDict, outputFile)

# This method will extract all of the UID, year pairs from the msd
def extractYearInfo_msd():
	# Reading in the MSD subset
	uidYearDict = {}
	with open("../Data/MSD Filtered Subset (1990-2010).csv", "r", encoding="utf-8") as msdCSV:
		
		# Iterate over each song in the MSD
		lineNum = 0
		for line in msdCSV:

			lineNum += 1
			song, artist, album, msdUID, year, artistID, artistMBID = line.split(",")
			uidYearDict[msdUID] = year

			# Every 5,000 songs, save the uidYearDict
			if ((lineNum % 5000) == 0):
				print("Saving the years of the first %d songs..." % lineNum)
				with open("../Data/UID-Year mappings - msd info.csv", "w", encoding="utf-8") as outputFile:
					dictToCsv(uidYearDict, outputFile)

		with open("../Data/UID-Year mappings - msd info.csv", "w", encoding="utf-8") as outputFile:
			dictToCsv(uidYearDict, outputFile)

# This method will extract all of the UID, year pairs from the billboard charts
# The year is the year associated w/ the first week the song appears on the charts
def extractYearInfo_billboard():
	
	# Setting up the uidYearDict
	uidYearDict = {}

	# Open the Billboard CSVs
	billboard1CSVPath = Path("../Data/Billboard-1990-2000.tsv")
	billboard2CSVPath = Path("../Data/Billboard-2000-2010.tsv")
	billboardCSVPaths = [billboard1CSVPath, billboard2CSVPath]
	for billboardCSVPath in billboardCSVPaths:

		# Open the file
		with open(billboardCSVPath, "r", encoding="utf-8") as billboardCSV:

			yearList = []
			lineNum = 0

			# Iterate over each line in the file
			for line in billboardCSV:

				# If this is the first line, populate the yearList dict
				lineNum += 1
				if (lineNum == 1):
					weekDates = line.split("\t")[3:-1]
					years = [int(x.split("/")[2]) for x in weekDates]
					years = list(reversed(years))
					yearList = years
					continue 

				# Otherwise, extract the info for the line
				splitLine = line.split("\t")
				song, artist, uid = splitLine[:3]
				weekList = list(reversed(splitLine[3:-1]))
				for weekNum, week in enumerate(weekList):
					if (week != "-1"):
						uidYearDict[uid] = yearList[weekNum]
						break

	with open("../Data/UID-Year mappings - billboard info.csv", "w", encoding="utf-8") as outputFile:
		dictToCsv(uidYearDict, outputFile)


# =========================
#        * MAIN * 
# =========================

# Extracting year info from the Genius .json's
print("\nExtracting year info from the Genius .json's...")
extractYearInfo_geniusJsons()

# Extracting year info from the msd
print("\nExtracting year info from the msd...")
extractYearInfo_msd()

# Extracting year info from the billboard charts
print("\nExtracting year info from the billboard charts...")
extractYearInfo_billboard()

# Creating a uidYearDict from all of the mappings in the CSVs
uidYearDict = {}
billboardMappingCSVPath = Path("../Data/UID-Year mappings - billboard info.csv")
geniusMappingCSVPath = Path("../Data/UID-Year mappings - genius info.csv")
msdMappingCSVPath = Path("../Data/UID-Year mappings - msd info.csv")
csvPaths = [billboardMappingCSVPath, geniusMappingCSVPath, msdMappingCSVPath]
for csvPath in csvPaths:

	print("Iterating through the mappings in %s" % str(csvPath))

	# Open the .csv file, and extract all of the mappings to the uidYearDict
	with open(csvPath, "r", encoding="utf-8") as csvFile:
		for line in csvFile:
			uid, year = [x.strip() for x in line.split(",")]
			uidYearDict[uid] = year

# Iterating through all of the songs in the .json dataset and adding years
print("\nIterating over each song to check if there's a UID, year mapping")
for songNum, songDict in enumerate(datasetDict["songs"]):

	# Grab the list of all of the UIDs associated w/ this song
	billboardUIDList = songDict["billboard_uid"]
	msdUIDList = songDict["msd_uid"]
	UIDs = billboardUIDList + msdUIDList
	
	# Iterate through each UID, and check the dict for a mapping
	for uid in UIDs:
		if (uid in uidYearDict):
			datasetDict["songs"][songNum]["year"] = uidYearDict[uid]
			break

# Save the new datasetDict to file
with open ("../Data/Genius Info - Billboard + MSD, 1990-2010 WITH YEARS.json", "w", encoding="utf-8") as jsonFile:
	json.dump(datasetDict, jsonFile)




