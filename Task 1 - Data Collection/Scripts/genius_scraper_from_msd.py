
# The following script was written by Trevor Hubbard; its main 
# purpose is to use the Genius API's functionality to search for
# song information on Genius


# =========================
#         SETUP
# =========================

# Some import statements
import requests, json, time, re
import pandas as pd
from pathlib import Path

# These variables will toggle on various debugging print statements if True
DEBUG = False
EXTRA = False

# Here are some global variables that'll be referenced throughout the script
songList = []
# Both of these dicts use the Geinus IDs as keys
artistDict = {}
producerDict = {}
usedIDs = set()


# =========================
#         CLASSES
# =========================

# =========================
#          METHODS
# =========================

# This method will print if "condition" is true
def print_if(message, condition):
	if (condition):
		print(message)

# This method will convert a JSON object to a formatted string
def jprint(jsonObject):
	print((json.dumps(jsonObject, sort_keys = True, indent = 4)))

# This method will save a given JSON object to disk
def saveJSON(jsonObject, saveName):
	jsonPath = saveName + ".json"
	with open(jsonPath, "w") as jsonFile:
		jsonFile.write(json.dumps(jsonObject, sort_keys = True, indent = 4))

# This method is to send a GET request to the Genius API
def genius_GET(method, payload):

	# This is the root URL of the Genius API
	rootURL = "https://api.genius.com/"

	# This is the URL with the method appended on it
	methodURL = rootURL + method 

	# Here, we'll define the headers for the GET request
	headers = {}
	headers["Authorization"] = "Bearer " + "aAhKtGY8NQGeqt5EhXdiE_EeXmmHREFY-xWIwB7KlrSds_cfU2jHQg8YUsrZ7trd"
	headers["User-Agent"] = "trevbook"

	# Now we can send the GET request
	request = requests.get(methodURL, headers=headers, params=payload)

	# Some debugging print statements
	print_if("\n===========================================", DEBUG)
	print_if("SENDING GET REQUEST W/ METHOD: %s" % method, DEBUG)
	print_if("Request URL: %s" % str(request.url), DEBUG)
	print_if("Request status code: %s" % str(request.status_code), DEBUG)
	print_if("===========================================\n", DEBUG)

	# Return the request
	return request

# This method is to return a pair: (DataFrame of the producers, new Song) if
# things work out correclty, or None if something goes wrong
def fieldSearch(songTitle, artist):

	# Prepare the GET request
	method = "search"
	payload = {"q": (songTitle + " " + artist)}
	request = genius_GET(method, payload)

	# Try to convert the GET request into a DataFrame
	try:
		df = pd.DataFrame(request.json()["response"]["hits"])
		df = pd.DataFrame(result for result in df["result"])
		with pd.option_context("display.max_rows", None, "display.max_columns", None):
			print_if("\nCreated the following DataFrame:\n", DEBUG and EXTRA)
			print_if("%s\n" % str(df), DEBUG and EXTRA)
		songID = (df.loc[0, "id"])
		songName = (df.loc[0, "title"])
		fieldsDF = FieldsFromSongID(songID)

		# Return the producer's DataFrame
		return (fieldsDF)

	# If an exception happens, return None
	except Exception as e:
		print_if("\nRan into the following exception while processing %s: \n%s\n" % (songTitle, str(e)), DEBUG)
		return None

# This method retrieves information for the given song ID, and returns a dataframe
# of that information (or None if an exception is run into)
def FieldsFromSongID(songID):

	# Declaring which attributes to scrape, and a dict to store them
	fieldsToScrape = ["annotation_count","api_path","apple_music_id","embed_content","featured_video","id","path","recording_location","release_date","song_art_image_thumbnail_url","song_art_image_url","stats","title","url","album","custom_performances","featured_artists","media","primary_artist","producer_artists","writer_artists"]
	fieldDict = {}
	for field in fieldsToScrape:
		fieldDict[field] = "<NONE>"

	# Prepare the GET request; these ones don't use a payload for
	# whatever reason, so I'll just send it as a method
	method = "songs/" + str(songID)
	payload = {}
	request = genius_GET(method, payload)

	# This will try to return a DataFrame of the producer artists
	try:
		for field in fieldsToScrape:
			if (field in request.json()["response"]["song"]):
				fieldDict[field] = request.json()["response"]["song"][field]

		# Convert fieldDict into a DataFrame, and return it
		return(fieldDict)

	# If it runs into an exception, it'll return None and print the error
	except Exception as e:
		print_if("\nRan into the following exception while processing songID #%s: \n%s\n" % (str(songID), str(e)), DEBUG)
		return fieldDict

# This method essentially combines the fieldSearch w/ the saveJSON method, 
# and will search Genius for a given artist and then save a JSON of the info scraped
def saveSearchResults(songTitle, artist, saveName):
	searchResults = fieldSearch(songTitle, artist)
	if (not searchResults is None):
		saveJSON(searchResults, saveName)
	else:
		print("Ran into an issue while searching Genius for %s by %s\n" % (songTitle, artist))

# =========================
#           MAIN 
# =========================

# Figure out which songs have already been scraped
scrapedSongsPath = Path("C:\\Data\\College\\CS 682 - Neural Networks\\Project\\GitHub\\CS-682-Hit-Song-Science-Project\\Task 1\\Data\\scraped genius (1990)")
scrapedSongsList = []
for child in scrapedSongsPath.iterdir():
	scrapedSongsList.append(child.stem)

# Load the msd set into a DataFrame
msdPath = "C:\\Data\\College\\CS 682 - Neural Networks\\Project\\GitHub\\CS-682-Hit-Song-Science-Project\\Task 1\\Data\\msd - songs from 1990-2000.csv"
endpointFound = True
with open(msdPath, "r", encoding="utf-8") as msdFile:
	for lineNum, line in enumerate(msdFile):

		# Skipping the song if this is the header row
		if (lineNum == 0): continue

		# Scraping the song information from this row
		rowFields = (line.split(","))
		title, artist, release, songID, year, artistID, artistMBID = [x.strip() for x in rowFields]

		# If we've already scraped info for this song, continue on
		# if (songID == "SOUYFTK12A8C13C821"):
		# 	endpointFound = True
		if (songID in scrapedSongsList):
			print("[%d / 124812] We've already scraped %s (%s)" % (lineNum, title, artist))
			continue

		# Remove any parentheses from this song
		titleParens = re.search('\(.*\)', title)
		if (titleParens):
			if (titleParens.span()[0] == 0): pass
			else:
				oldTitle = title
				title = title[:titleParens.span()[0]]
				print("\nChanged %s to %s\n" % (oldTitle, title))
		print("[%d / 124812] Searching for song %s: %s by %s" % (lineNum, songID, title, artist))
		savePath = "C:\\Data\\College\\CS 682 - Neural Networks\\Project\\GitHub\\CS-682-Hit-Song-Science-Project\\Task 1\\Data\\scraped genius (1990)\\" + songID
		saveSearchResults(title, artist, savePath)
		time.sleep(.5)