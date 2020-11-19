
# This neural network was written by Trevor Hubbard; it performs Hit Song
# Prediction using vector embeddings of a music-industry co-collaboration network

# =========================
#        * SETUP *
# =========================

# Some import statements
import torch
import random
import numpy as np
import torch.nn as nn
import torch.optim as optim
from torch.utils.data.sampler import SubsetRandomSampler

# Setting up Pytorch's use of CUDA 
device = torch.device("cuda")

# =========================
#       * CLASSES *
# =========================

# This class will be used to help in the song data! 
class SongDataset(torch.utils.data.Dataset):

	# The init method defines how we'll input the data; 
	def __init__(self, tsvFilePath):

		# Declare some variables that we'll use throughout the init
		xHit = []
		xNotHit = []

		# Open the tsv and process the data in it
		with open(tsvFilePath, "r", encoding="utf-8") as tsvFile:

			# Iterate through each line of the .tsv and store the info
			for lineNum, line in enumerate(tsvFile):

				line = line.strip()

				# If we're on the first line, figure out where the "hit" column is
				if (lineNum == 0): 
					splitLine = line.split("\t")
					for idx, header in enumerate(splitLine):
						if (header == "hit"):
							hitCol = idx
							break
					continue

				# If we're looking at a hit, append it to xHit; otherwise, to xNotHit
				splitLine = line.split("\t")
				if (int(splitLine[hitCol]) == 1):
					xHit.append([float(x) for x in splitLine[hitCol+1:]])
				else:
					xNotHit.append([float(x) for x in splitLine[hitCol+1:]])

		# Create xList and yList from the hits a random sample of the nonHits 
		xNotHit_sample = random.choices(xNotHit, k=len(xHit))
		xList = xHit + xNotHit_sample
		yList = [1 for x in range(len(xHit))] + [0 for x in range(len(xNotHit_sample))]

		# Convert xList and yList to Tensors
		self.x_data = torch.tensor(xList, dtype=torch.float32, device="cuda")
		self.y_data = torch.tensor(yList, dtype=torch.float32, device="cuda")

	# The len method returns the length of x_data
	def __len__(self):
		return len(self.x_data)

	# The getitem method will specify how to return a particular index
	def __getitem__(self, idx):
		if (torch.is_tensor(idx)):
			idx = idx.tolist()
		emb = self.x_data[idx]
		hit = self.y_data[idx]
		sample = (emb, hit)
		return sample

# =========================
#       * METHODS * 
# =========================

# This method will check the accuracy of the model using data from the loader
def checkAccuracy(loader, model):

	num_correct = 0
	num_samples = 0
	model.eval()
	with torch.no_grad():
		for x, y in loader:
			binaryScores = torch.round(torch.sigmoid(model(x))).reshape(y.shape)
			# print("Checking accuracy... scores is %s" % binaryScores)
			num_correct += (y == binaryScores).sum().float()
			num_samples += len(y)
		return (num_correct/num_samples)

# =========================
#        * MAIN * 
# =========================

# Creating the Dataset from the song embedding .tsv
print("\nReading in the dataset...")
songTsvPath = "C:\\Data\\College\\CS 682 - Neural Networks\\Project\\Task 3 - Network Development\\Data\\Song Embeddings - 128 dim.tsv"
songs = SongDataset(songTsvPath)
print("Finished reading in the dataset!\n")

# Creating the training / validation split 
validationSplit = .2
songAmt = len(songs)
splitIdx = int(np.floor(songAmt * validationSplit))
indices = list(range(songAmt))
np.random.shuffle(indices)
trainIndices = indices[splitIdx:]
valIndices = indices[:splitIdx]

# Creating the Samplers and DataLoaders for the train & validation data
sampler_train = SubsetRandomSampler(trainIndices)
sampler_val = SubsetRandomSampler(valIndices)
loader_train = torch.utils.data.DataLoader(songs, batch_size=64, sampler=sampler_train)
loader_val = torch.utils.data.DataLoader(songs, batch_size=64, sampler=sampler_val)

# Get the embedding dimension from one of the samples
embedding_dim = (len(songs[0][0]))

# Define a model using nn.Sequential
hidden_amt_1 = 1024
hidden_amt_2 = 512
hidden_amt_3 = 256
hidden_amt_4 = 32
model = nn.Sequential(nn.Linear(embedding_dim, hidden_amt_1),
					  nn.ReLU(),
					  nn.BatchNorm1d(hidden_amt_1),
					  nn.Linear(hidden_amt_1, hidden_amt_2),
					  nn.ReLU(),
					  nn.BatchNorm1d(hidden_amt_2),
					  nn.Linear(hidden_amt_2, hidden_amt_3),
					  nn.ReLU(),
					  nn.BatchNorm1d(hidden_amt_3),
					  nn.Linear(hidden_amt_3, hidden_amt_4),
					  nn.ReLU(),
					  nn.BatchNorm1d(hidden_amt_4),
					  nn.Linear(hidden_amt_4, 1))

# Set some hyperparameters for the model
epochs = 1000
learning_rate = 0.000005

# Train the model
model = model.to("cuda")
optimizer = optim.Adam(model.parameters(), lr=learning_rate)
for e in range(epochs):
	for idx, (x, y) in enumerate(loader_train):
		
		# Indicate that we're in training mode
		model.train()

		# Calculate the score, and perform the backwards pass
		scores = model(x)
		scores = scores.reshape(y.shape)

		loss_fn = nn.BCEWithLogitsLoss()
		loss = loss_fn(scores, y)
		optimizer.zero_grad()
		loss.backward()
		optimizer.step()

	# Check the accuracy every epoch
	valAccuracy = checkAccuracy(loader_val, model)
	trainAccuracy = checkAccuracy(loader_train, model)
	print("Epoch %d: %.4f val accuracy" % (e, valAccuracy))
	print("Epoch %d: %.4f train accuracy\n" % (e, trainAccuracy))