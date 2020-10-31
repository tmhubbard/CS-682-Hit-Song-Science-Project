
# The following script was written by Trevor Hubbard; its main 
# purpose is to collect various statistics about the data I've
# scraped from Genius for this project

# =========================
#         SETUP
# =========================

# Some import statements
import random, json, time
import pandas as pd
from pathlib import Path

# Some parameters for the statistics search
SONG_AMT = 10000
ALL_SONGS = True

# =========================
#          METHODS
# =========================

# This method will convert a JSON object to a formatted string
def jprint(jsonObject):
	print((json.dumps(jsonObject, sort_keys = True, indent = 4)))

# =========================
#           MAIN 
# =========================

# Randomly selecting which songs to calculate statistics for
songInfoPath = Path(input("\nEnter the path containing the .json's: "))
songIDList = []
curTime = time.time()
print("\nSelecting a sample of %d songs from the folder of .json files..." % SONG_AMT)
for childFile in songInfoPath.iterdir():
	songIDList.append(childFile.stem)
sampledSongIDs = []

# If you have the allSongs flag enabled, just calculate stats for all of the songs;
# otherwise, calculate statistics for SONG_AMT random songs
if (ALL_SONGS):   
	sampledSongIDs = random.choices(songIDList, k = len(songIDList))
	SONG_AMT = len(songIDList)
else:
	sampledSongIDs = random.choices(songIDList, k = SONG_AMT)
print("Finished selecting the sample! It took %.2f seconds.\n" % (time.time()-curTime))

# Declaring some variables to help count the prevalence of various fields
attributeList = ["annotation_count","api_path","apple_music_id","embed_content","featured_video","id","path","recording_location","release_date","song_art_image_thumbnail_url","song_art_image_url","stats","title","url","album","custom_performances","featured_artists","media","primary_artist","producer_artists","writer_artists"]


def songStatsForYear(year, allYears=False):

	attributeTypeList = [int,str,str,str,bool,int,str,str,str,str,str,dict,str,str,dict,list,list,list,dict,list,list]
	attributeTypeDict = {} # attribute --> expected type in JSON
	attributeCountDict = {} # attribute --> the count for a given attribute (some attributes have more per song)
	attributePrevalenceDict = {} # attribute --> how many JSON's contained a valid entry
	dictAttDict = {} # attribute (expected type dict) --> the keys that I've found for that dict
	listAttDict = {} # attribute (expected type list) --> the different lengths of lists I've found
	listAttDict_keys = {} # attribute (expected type list) --> the different keys I've found for the dicts in the lists
	custom_performances_labelCount = {} # custom performance label --> the amount of JSONs that have this type of custom performance
	idList = [] # a list of the Genius IDs I find along the way
	annotationCountList = [] # a list of the number of annotations for each song that has them

	# Doing more work to set up these field variables
	for attNum, attribute in enumerate(attributeList):
		attributeCountDict[attribute] = 0
		attributeTypeDict[attribute] = attributeTypeList[attNum]
		if ((attributeTypeList[attNum] == dict)):
			dictAttDict[attribute] = {}
		if ((attributeTypeList[attNum] == list)):
			listAttDict[attribute] = []
			listAttDict_keys[attribute] = {}

	# Tallying up the attribute appearance for each attribute
	SONG_AMT_YEAR = 0
	curTime = time.time()
	print("Now, I'm parsing through the .json, counting the values of each attribute.")
	for songID in sampledSongIDs:
		with open((songInfoPath / Path(songID + ".json")), "r") as songJSON:
			songData = json.load(songJSON)

			if (not allYears):
				if (not "release_date" in songData):
					continue
				if ((songData["release_date"] is None)):
					continue
				if ((not songData["release_date"].split("-")[0] == str(year))):
					continue
			SONG_AMT_YEAR += 1

			for attNum, attribute in enumerate(attributeList):

				# If we're looking at annotation_count, then count how many we have more than one annotation for
				if(attribute == "annotation_count"):
					annotationCountList.append(songData[attribute])
					if (songData[attribute] > 0):
						attributeCountDict[attribute] += 1

				# If we're looking at featured_video, then count how many we have a featured video fo
				elif(attribute == "featured_video"):
					if (songData[attribute]):
						attributeCountDict[attribute] += 1

				# If we're looking at id, then count how often we've got a non-negative int
				elif(attribute == "id"):
					if (isinstance(songData[attribute], int) and songData[attribute] > 0):
						attributeCountDict[attribute] += 1
						idList.append(songData[attribute])

				# If the attribute is a list, we'll count how often it's not empty 
				elif (isinstance(songData[attribute], list)):
					if (len(songData[attribute]) > 0):
						attributeCountDict[attribute] += 1
						listAttDict[attribute].append(len(songData[attribute]))

						# Collect information about each of the keys of the dicts in the list
						for listDict in songData[attribute]:
							for key in listDict.keys():
								if (not key in listAttDict_keys[attribute]):
									listAttDict_keys[attribute][key] = 0
								listAttDict_keys[attribute][key] += 1

						# If we're looking at custom_performances, figure out what labels we can have
						if (attribute == "custom_performances"):
							for listDict in songData[attribute]:
								if (not listDict["label"] in custom_performances_labelCount):
									custom_performances_labelCount[listDict["label"]] = 0
								custom_performances_labelCount[listDict["label"]] += 1

				# If the attribute is a dict, then we'll count how often it has more than one key
				elif (isinstance(songData[attribute], dict)):
					if (len(list(songData[attribute].keys())) > 0):
						attributeCountDict[attribute] += 1
						for key in songData[attribute].keys():
							if (not key in dictAttDict[attribute]):
								dictAttDict[attribute][key] = 0
							dictAttDict[attribute][key] += 1

				# If the attribute is a str, then we'll count it if it's not empty
				elif (isinstance(songData[attribute], str)):
					if (not songData[attribute] == ""):
						attributeCountDict[attribute] += 1


	print("Finished parsing the json! It took %.2f seconds. We found %d songs\n" % ((time.time()-curTime), SONG_AMT_YEAR))				

	# Print the statistics for the attribute counts
	for attribute in attributeCountDict.keys():

		# If the attribute is supposed to be a dict, then print more info about the dict
		if (attributeTypeDict[attribute] == dict):
			print("\n%s\n================\nprevalence: %.2f%%\n\n" % (attribute, (attributeCountDict[attribute]/SONG_AMT_YEAR)*100))
			print("Since this attribute is a dict, I collected stats about the keys I found...")
			for key in dictAttDict[attribute].keys():
				# print("%s: %.2f%%" % (key, (dictAttDict[attribute][key]/attributeCountDict[attribute])*100))
				print("- %s" % (key))
			print()

		# If the attribute is supposed to be a list, print more info about the list
		elif (attributeTypeDict[attribute] == list):

			# Print some info about the various different sizes of each list
			print("\n%s\n================\nprevalence: %.2f%%" % (attribute, (attributeCountDict[attribute]/SONG_AMT_YEAR)*100))
			print("Since this attribute is a list, I collected some stats about the length of the list...")
			print("min list size: %d" % min(listAttDict[attribute]))
			print("max list size: %d" % max(listAttDict[attribute]))
			print("avg list size: %.0f" % (sum(listAttDict[attribute])/len(listAttDict[attribute])))
			print("\n")

			# Print some info about the keys I found in the list
			print("The elements in the list are dicts. Here are the keys I found in each:")
			for key in listAttDict_keys[attribute].keys():
				print("- %s" % key)

			# If this is the custom_performances attribute, print some of the labels
			if (attribute == "custom_performances"):
				print("\nAs follows are the labels I found (and their counts):")
				sortedDict = {k: v for k, v in sorted(custom_performances_labelCount.items(), key=lambda item: item[1], reverse=True)}
				print("\nIn total, there were %d unique labels..." % len(list(sortedDict.keys())))
				labelPrint = 0
				with open("labels.txt", "w", encoding="utf-8") as labelFile:
					for label in sortedDict.keys():
						labelFile.write("%s: %d\n" % (label, sortedDict[label]))
						labelPrint += 1
		
		# Otherwise, just print some info about the attribute
		else:
			print("\n\n%s\n================\nprevalence: %.2f%%" % (attribute, (attributeCountDict[attribute]/SONG_AMT_YEAR)*100))

			# If this is the ID attribute, print some stats about it
			if (attribute == "id"):
				print("Min ID found: %d" % min(idList))
				print("Max ID found: %d\n\n" % max(idList))

			# If this is the annotation_count attribute, print some stats about it
			if (attribute == "annotation_count"):
				print("Min # of annotations: %d" % min(annotationCountList))
				print("Max # of annotations: %d" % max(annotationCountList))
				print("Avg # of annotations: %.0f" % (sum(annotationCountList)/len(annotationCountList)))

				# Create data for annotation count histogram
				annotationCtDict = {}
				for ct in annotationCountList:
					if (not ct in annotationCtDict):
						annotationCtDict[ct] = 0
					annotationCtDict[ct] += 1
				sortedDict = {k: v for k, v in sorted(annotationCtDict.items(), key=lambda item: item[0])}
				print("\nHere are some counts for making a histogram:")
				for ct in sortedDict.keys():
					print("%d, %d" % (ct, sortedDict[ct]))

			# If this is the release_date attribute, print some stats about it

	outputDict = {}
	for attribute in attributeCountDict.keys():
		print("%s: %.4f" % (attribute, (attributeCountDict[attribute]/SONG_AMT_YEAR)))
		outputDict[attribute] = float("%.4f" % (attributeCountDict[attribute]/SONG_AMT_YEAR))
	return outputDict


# bigDict = {}
# bigDict["year"] = []
# for attribute in attributeList:
# 	bigDict[attribute] = []
# for curYear in range(2000, 2011):
# 	print("SEARCHING FOR %d" % curYear)
# 	statDict = songStatsForYear(curYear)
# 	for attribute in statDict.keys():
# 		bigDict[attribute].append(statDict[attribute])
# 	bigDict["year"].append(curYear)
# pd.DataFrame.from_dict(bigDict).to_excel("result.xlsx", index=False)


print((songStatsForYear(None, True)))
	