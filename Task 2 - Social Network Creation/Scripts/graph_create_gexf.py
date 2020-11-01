
# Some import statements
import datetime
import lxml.etree as ET
import pandas as pd

# Set an "expiration date" for when the author nodes will disappear
exiprationMonths = 12

# Setting up the XML ElementTree 
attr_qname = ET.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
gexf = ET.Element('gexf', 
                 {attr_qname: 'http://www.gexf.net/1.3draft  http://www.gexf.net/1.3draft/gexf.xsd'}, 
                 nsmap={None: 'http://graphml.graphdrawing.org/xmlns/graphml'},
                 version='1.3')
graph = ET.SubElement(gexf,'graph', defaultedgetype='undirected', mode='dynamic', timeformat="date")
nodeAttributes = ET.SubElement(graph, "attributes", {"class": "node"})
attributes = ET.SubElement(graph, "attributes", {"class": "edge"})
nodes = ET.SubElement(graph, "nodes")
edges = ET.SubElement(graph, "edges")

# Setting up each of the edge attributes
for attID, attribute in enumerate(attributeList):
	graphAttribute = ET.SubElement(attributes, "attribute", id=str(attID), title=attribute, type="string")
maxPortolioAttribute = ET.SubElement(attributes, "attribute", id=str(len(attributeList)), title="edgePortfolio", type="string")

# Create a dict of authors and their appearances
authorAppearanceDict = {}
for rowIdx, row in excelDF.iterrows():

    # Split the list of authors, and add the record's publication date as a value
    # in the array associated with each author in authorAppearanceDict
    authors = row["author"].split(";")
    for author in authors:
        if (author not in authorAppearanceDict):
            authorAppearanceDict[author] = []
        authorAppearanceDict[author].append(row["Publication Date"].date())

# Create the expiration dates for each of the authors
authorExpirationDict = {}
for author in authorAppearanceDict.keys():
	dateList = sorted(authorAppearanceDict[author])
	
	# Make the expiration date expirationMonths months after the last instance
	expirationDate = dateList[-1] + datetime.timedelta(exiprationMonths * 30)
	authorExpirationDict[author] = expirationDate


# Figure out the first date associated with each author
authorDebutDict = {}
for author in authorAppearanceDict.keys():
    authorDebutDict[author] = min(authorAppearanceDict[author])

# Create a node for each of the authors
authorNodes = {}
authorIDs = {}
authorNames = {}
for authorID, author in enumerate(authorDebutDict.keys()):
    authorIDs[author] = authorID
    authorNames[authorID] = author
    authorNodes[author] = ET.SubElement(nodes, "node", id=str(author), label=author, start=str(authorDebutDict[author]), end=str(authorExpirationDict[author]))

# Create a dict of all of the links between authors
edgeDict = {}
for rowIdx, row in excelDF.iterrows():

	# Iterate through each pair of authors in the database
	authors = row["author"].split(";")
	for author in authors:
		for otherAuthor in authors:
			
			# Skip if you're looking at a connection between an author and themselves
			if (author == otherAuthor): continue

			# Check to see if the pair of authors is in the edgeDict
			authorID = authorIDs[author]
			otherAuthorID = authorIDs[otherAuthor]
			authorPairKey = (authorID, otherAuthorID)

			# Check if (otherAuthor, author) is a key in the dict
			if ((otherAuthorID, authorID) in edgeDict):
				authorPairKey = (otherAuthorID, authorID)

			# Check if (author, otherAuthor) is a key in the dict
			elif((authorID, otherAuthorID) in edgeDict):
				authorPairKey = (authorID, otherAuthorID)

			# If the pair isn't in the edgeDict, make a new attributeDict for them 
			else:
				edgeDict[(authorID, otherAuthorID)] = {}
				for attribute in attributeList:
					edgeDict[(authorID, otherAuthorID)][attribute] = []
				authorPairKey = (authorID, otherAuthorID)

			# Skip adding the information if you've already added it 
			if (len(edgeDict[authorPairKey]["docid"]) > 0 and edgeDict[authorPairKey]["docid"][-1] == row["docid"]):
				continue

			# Otherwise, update the attributeDict for those authors
			else:
				for attribute in attributeList:
					rowData = row[attribute]
					edgeDict[authorPairKey][attribute].append(rowData)

# Create an edge for each of the author pairs in the edgeDict
graphEdges = {}
for edgeID, edgePair in enumerate(edgeDict.keys()):
	edgeDict[edgePair]["Publication Date"] = [x.date() for x in edgeDict[edgePair]["Publication Date"]]
	attDict = edgeDict[edgePair]
	firstDate = min(attDict["Publication Date"])
	expirationDate = max(attDict["Publication Date"]) + datetime.timedelta(exiprationMonths * 30)
	curEdge = ET.SubElement(edges, "edge", 
										 id=str(edgeID), 
										 source=str(authorNames[edgePair[0]]), 
										 target=str(authorNames[edgePair[1]]), 
										 label=str(attDict["docid"]), 
										 start=str(firstDate), 
										 end=str(expirationDate),
										 weight=str(len(attDict["docid"])))
	attributeElement = ET.SubElement(curEdge, "attvalues")
	graphAttributes = {}
	for attID, attribute in enumerate(attributeList):
		graphAttributes[attribute] = ET.SubElement(attributeElement, "attvalue", {"for": str(attID), "value": (";".join([str(x) for x in attDict[attribute]]))})

	# Figuring out what the most represented portfolio was for this author pair
	splitPortfolioList = attDict["portfolio"]
	portfolioDict = {}
	for portfolio in splitPortfolioList:
		if (portfolio not in portfolioDict):
			portfolioDict[portfolio] = 0
		portfolioDict[portfolio] += 1
	portfolioDict = {k: v for k, v in sorted(portfolioDict.items(), key=lambda item: item[1], reverse=True)}
	maxPortfolio = list(portfolioDict.keys())[0]
	graphAttributes["maxPortfolio"] = ET.SubElement(attributeElement, "attvalue", {"for": str(len(attributeList)), "value": str(maxPortfolio)})

# Writing the ElementTree to a .gexf file
tree = ET.ElementTree(gexf)
tree.write("testGraph.gexf")