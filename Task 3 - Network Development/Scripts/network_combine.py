
# This neural network was written by Trevor Hubbard; it performs Hit Song
# Prediction using vector embeddings of a music-industry co-collaboration network

# =========================
#        * SETUP *
# =========================

# Some import statements
import torch, json, random, time
import numpy as np
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data.sampler import SubsetRandomSampler

# Setting up Pytorch's use of CUDA 
device = torch.device("cuda")

# =========================
#       * CLASSES *
# =========================

# This class will be used to help in the song data! 
class SongDataset(torch.utils.data.Dataset):

	# The init method defines how we'll input the data; 
	def __init__(self, embeddingTsvPath, audioJsonPath):

		# This dictionary will hold all of the data
		self.songDict = {}

		curTime = time.time()
		print("\nReading the network embeddings from the .tsv...")

		# Open the tsv and process the data in it
		with open(embeddingTsvPath, "r", encoding="utf-8") as tsvFile:
			
			# Iterate through each line of the .tsv and store the info
			hitCol = 0
			idCol = 0
			for lineNum, line in enumerate(tsvFile):

				line = line.strip()
				splitLine = line.split("\t")

				# If we're on the first line, figure out where the "hit" column is
				if (lineNum == 0): 
					for idx, header in enumerate(splitLine):
						if (header == "songID"):
							idCol = idx
						if (header == "hit"):
							hitCol = idx
					continue

				# Add the song to the songDict
				songID = int(splitLine[idCol])
				curHit = int(splitLine[hitCol])
				if (not songID in self.songDict):
					self.songDict[songID] = {"hit": curHit, "embedding": None, "audio features": None}

				# Update the song's embedding 
				self.songDict[songID]["embedding"] = torch.tensor([float(x) for x in splitLine[hitCol+1:]], dtype=torch.float32, device="cuda")

		print("Finished reading in the embeddings! It took %.3f seconds" % (time.time()-curTime))
		curTime = time.time()
		print("\nReading in the Spotify data from the .json...")

		# Open the audio features JSON and process the data in it
		with open(audioJsonPath, "r", encoding="utf-8") as jsonFile:
			songData = json.load(jsonFile)["songs"]
			features = ['duration_ms', 'key', 'mode', 'time_signature', 'acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'valence', 'tempo']
			for song in songData:
				songID = int(song["title"][1])
				curHit = int(song["hit"])
				if (song["audio_features"] not in [{}, None]):
					if (songID not in self.songDict):
						self.songDict[songID] = {"hit": curHit, "embedding": None, "audio features": None}
					self.songDict[songID]["audio features"] = torch.tensor([song['audio_features'][feature] for feature in features], dtype=torch.float32, device="cuda")

		print("Finished reading in the .json! It took %.3f seconds" % (time.time()-curTime))

		# Remove any songs that don't have both an embedding and audio features
		curTime = time.time()
		print("\nRemoving songs without both an embedding and audio features...")
		hitCount = 0
		idsToRemove = []
		for songNum, songID in enumerate(self.songDict.keys()):
			song = self.songDict[songID]
			if ((song["embedding"] is None) or (song["audio features"] is None)):
				idsToRemove.append(songID)
				continue
			else:
				if (song["hit"] == 1): hitCount += 1
		for songID in idsToRemove:
			del self.songDict[songID]
		print("Finished removing the songs! It took %.3f seconds." % (time.time()-curTime))

		# Creating the songList (a list version of the songDict)
		shuffledSongDict = list(self.songDict.keys())
		np.random.shuffle(shuffledSongDict)
		self.songList = []
		nonHitCount = 0
		for songID in shuffledSongDict:
			song = self.songDict[songID]
			
			# Skip if this is a nonHit and we've already added all of those
			if (nonHitCount == hitCount and song["hit"] == 0):
				continue

			self.songList.append(song)
			self.songList[-1]["id"] = songID

			if (song["hit"] == 0):
				nonHitCount += 1

	# The len method returns the length of x_data
	def __len__(self):
		return len(self.songList)

	# The getitem method will specify how to return a particular index
	def __getitem__(self, idx):
		if (torch.is_tensor(idx)):
			idx = idx.tolist()
		song = self.songList[idx]
		songID = song["id"]
		emb = song["embedding"]
		audio_features = song["audio features"]
		hit = torch.tensor(song["hit"], dtype=torch.float32, device="cuda")
		return (songID, emb, audio_features, hit)

# This class is the Two Layer Net that we use for the audio features model
class TwoLayerFC(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        nn.init.kaiming_normal_(self.fc1.weight)
        self.fc2 = nn.Linear(hidden_size, num_classes)
        nn.init.kaiming_normal_(self.fc2.weight)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        scores = self.fc2(x)
        return scores

# =========================
#       * METHODS * 
# =========================

# This method will check the accuracy of the model using data from the loader
def checkAccuracy(loader, model, modelType):

	num_correct = 0
	num_samples = 0
	model.eval()
	with torch.no_grad():
		for (songID, emb, audio_features, hit) in loader:
			binaryScores = []
			if (modelType == "emb"):
				binaryScores = torch.round(torch.sigmoid(model(emb))).reshape(hit.shape)
			elif (modelType == "audio"):
				binaryScores = torch.round(torch.sigmoid(model(audio_features))).reshape(hit.shape)
			num_correct += (hit == binaryScores).sum().float()
			num_samples += len(hit)
		return (num_correct/num_samples)

# =========================
#        * MAIN * 
# =========================

# Creating the Dataset from the song embedding .tsv
songTsvPath = "C:\\Data\\College\\CS 682 - Neural Networks\\Project\\Task 3 - Network Development\\Data\\Song Embeddings - 128 dim.tsv"
songJsonPath = "C:\\Data\\College\\CS 682 - Neural Networks\\Project\\Task 1 - Data Collection\\Data\\Genius Info + Spotify Features, 1990-2010.json"
songs = SongDataset(songTsvPath, songJsonPath)

# Iterating through each of the songs to check if they're constructed correctly
_, emb, audio_features, _ = songs[0]
audioDimCount = len(audio_features)
embDimCount = len(emb)
print("The length of the songs dataset is %d" % len(songs))

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

# Define the embedding model using nn.Sequential
embHidden1 = 1024
embHidden2 = 512
embHidden3 = 256
embHidden4 = 32
embModel = nn.Sequential(nn.Linear(embDimCount, embHidden1),
					  nn.ReLU(),
					  nn.BatchNorm1d(embHidden1),
					  nn.Linear(embHidden1, embHidden2),
					  nn.ReLU(),
					  nn.BatchNorm1d(embHidden2),
					  nn.Linear(embHidden2, embHidden3),
					  nn.ReLU(),
					  nn.BatchNorm1d(embHidden3),
					  nn.Linear(embHidden3, embHidden4),
					  nn.ReLU(),
					  nn.BatchNorm1d(embHidden4),
					  nn.Linear(embHidden4, 1))

# Define the audio model using nn.Sequential
audioHidden = 64
# audioModel = nn.Sequential(nn.Linear(audioDimCount, audioHidden),
# 						   nn.ReLU(),
# 						   nn.Linear(audioHidden, 1))
audioModel = TwoLayerFC(audioDimCount, audioHidden, 1)

# Set some hyperparameters for the model
epochs = 1000
embLR = 0.00001
audioLR = 0.0005

# Train the models
embModel = embModel.to("cuda")
audioModel = audioModel.to("cuda")
embOptimizer = optim.Adam(embModel.parameters(), lr=embLR)
audioOptimizer = optim.Adam(audioModel.parameters(), lr=audioLR)
for e in range(epochs):
	for idx, (songID, emb, audio_features, hit) in enumerate(loader_train):
		
		# Indicate that we're in training mode
		embModel.train()
		audioModel.train()

		# Declaring a loss function
		loss_fn = nn.BCEWithLogitsLoss()

		# # Perform a training step for the embedding model 
		# embScores = embModel(emb)
		# embScores = embScores.reshape(hit.shape)
		# embLoss = loss_fn(embScores, hit)
		# embOptimizer.zero_grad()
		# embLoss.backward()
		# embOptimizer.step()

		# Perform a training step for the audio model
		print(audio_features)
		audioScores = audioModel(audio_features)
		audioScores = audioScores.reshape(hit.shape)
		print(audioScores)
		print(hit)
		audioLoss = loss_fn(audioScores, hit)
		audioOptimizer.zero_grad()
		audioLoss.backward()
		audioOptimizer.step()

	# # Print the accuracy of the embedding model
	# embValAcc = checkAccuracy(loader_val, embModel, "emb")
	# embTrainAcc = checkAccuracy(loader_train, embModel, "emb")
	# print("\nEMBEDDING MODEL:")
	# print("Epoch %d: %.4f val accuracy" % (e, embValAcc))
	# print("Epoch %d: %.4f train accuracy\n" % (e, embTrainAcc))

	# Print the accuracy of the audio model
	audioValAcc = checkAccuracy(loader_val, audioModel, "audio")
	audioTrainAcc = checkAccuracy(loader_train, audioModel, "audio")
	print("\nAUDIO MODEL:")
	print("Epoch %d: %.4f val accuracy" % (e, audioValAcc))
	print("Epoch %d: %.4f train accuracy" % (e, audioTrainAcc))