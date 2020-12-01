
# This script will convert an .xlsx file to a .tsv (tab-separated values)

# =========================
#        * MAIN * 
# =========================

# Import statements
import pandas as pd
from pathlib import Path

# Ask the user to input the path to the .xlsx file
xlsxPath = Path(input("\nPlease enter the path to the .xlsx file: "))

# Convert the xlsx file to a DataFrame
xlsxDF = pd.read_excel(xlsxPath)

# Iterate through the DataFrame and write the tsv
tsvPath = xlsxPath.parent / Path(xlsxPath.stem + ".tsv")
with open(tsvPath, "w", encoding="utf-8") as tsvFile:

	# First, write the column row
	columnList = []
	for col in xlsxDF.columns:
		tsvFile.write("%s\t" % col)
		columnList.append(col)
	tsvFile.write("\n")

	# Now, iterate through each row, and write everything!
	for index, row in xlsxDF.iterrows():
		for col in list(row):
			tsvFile.write("%s\t" % col)
		tsvFile.write("\n")