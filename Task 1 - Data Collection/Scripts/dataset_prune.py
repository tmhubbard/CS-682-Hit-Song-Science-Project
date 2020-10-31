
# This script was written by Trevor Hubbard; its purpose is to prune the data 
# I scraped from Genius by copying the .json's that have been validated

# =========================
#        * SETUP *
# =========================

# Some import statements
from pathlib import Path
from shutil import copyfile

# Asking the user for a couple of things
inputFolder = Path(input("\nPlease enter the path to the folder of .json's to prune: "))
outputFolder = Path(input("\nPlease enter the path to the folder where you'd like to copy validated .json's to: "))
validationFilePath = Path(input("\nPlease enter the path to the .txt file that contains the songID, validation pairs: "))


# =========================
#        * MAIN * 
# =========================

# Opening the validation file and iterating through the songs in it 
with open(validationFilePath, "r") as validationFile:
	for line in validationFile:
		songID, val = [x.strip() for x in line.split(":")]
		val = int(val)
		if (val == 1):
			songJSON = inputFolder / Path(songID + ".json")
			outputJSON = outputFolder / Path(songID + ".json")
			copyfile(songJSON, outputJSON)




