import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from torch.utils.data.sampler import WeightedRandomSampler, SubsetRandomSampler
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix

import torchvision.transforms as T
import matplotlib.pyplot as plt

import numpy as np
from tqdm import tqdm

import json

print("Loading JSON")
spotifyPath = "C:\Data\College\CS 682 - Neural Networks\Project\Task 1 - Data Collection\Data\Spotify Features, 1990-2010.json"
with open(spotifyPath, 'r', encoding='utf-8') as f:
    json_data = json.load(f)['songs']

print(json_data[0])
json_X = []
json_y = []
print("Building Dataset")
features = ['duration_ms', 'key', 'mode', 'time_signature', 'acousticness', 'danceability',
            'energy', 'instrumentalness', 'liveness', 'loudness', 'speechiness', 'valence',
            'tempo']
for i in tqdm(range(len(json_data))):
    if json_data[i]['audio_features'] not in [{}, None]:
        json_X.append([json_data[i]['audio_features'][feature] for feature in features])
        json_y.append(int(json_data[i]['hit']))

non_hit_to_hits = 1
class_sample_count = np.array([len(np.where(json_y == t)[0]) for t in np.unique(json_y)])
weight = [1, 0]
samples_weight = np.array([weight[t] for t in json_y])
subsample_idxs = list(WeightedRandomSampler(samples_weight, int(non_hit_to_hits*int(class_sample_count[1])), replacement=False))
subsample_idxs += [i for i in range(len(json_y)) if json_y[i] == 1]
json_X = [json_X[i] for i in subsample_idxs]
json_y = [json_y[i] for i in subsample_idxs]

X_train, X_val, y_train, y_val = train_test_split(json_X, json_y, test_size=0.20, stratify=json_y)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.fit_transform(X_val)

batch_size = 32

dataset_train = TensorDataset(torch.Tensor(X_train), torch.Tensor(y_train))
loader_train  = DataLoader(dataset_train, batch_size=batch_size, sampler=SubsetRandomSampler(range(len(X_train))))

dataset_val   = TensorDataset(torch.Tensor(X_val), torch.Tensor(y_val))
loader_val    = DataLoader(dataset_val, batch_size=batch_size, sampler=SubsetRandomSampler(range(len(X_val))))

USE_GPU = True
dtype = torch.float32
if USE_GPU and torch.cuda.is_available():
    device = torch.device('cuda')
else:
    device = torch.device('cpu')

print_every = 100

plot_x = []
plot_y = []

def random_weight(shape):
    if len(shape) == 2:
        fan_in = shape[0]
    else:
        fan_in = np.prod(shape[1:])

    w = torch.randn(shape, device=device, dtype=dtype) * np.sqrt(2. / fan_in)
    w.requires_grad = True
    return w

def zero_weight(shape):
    return torch.zeros(shape, device=device, dtype=dtype, requires_grad=True)

def check_accuracy(loader, model, is_train):
    num_correct = 0
    num_samples = 0
    model.eval()  # set model to evaluation mode
    with torch.no_grad():
        total_preds = []
        total_y = []
        for x, y in loader:
            x = x.to(device=device, dtype=dtype)  # move to device, e.g. GPU
            y = y.to(device=device, dtype=dtype)
            scores = model(x)
            preds = torch.round(torch.sigmoid(scores)).squeeze()
            total_preds += preds.tolist()
            total_y += y.tolist()
            num_correct += (preds == y).sum().float()
            num_samples += y.size(0)
        acc = float(num_correct) / num_samples
        print('Got %d / %d correct (%.2f)' % (num_correct, num_samples, 100 * acc))
        return (acc, confusion_matrix(total_y, total_preds))

def train(model, optimizer, epochs=1):
    model = model.to(device=device)  # move the model parameters to CPU/GPU
    for e in range(epochs):
        for t, (x, y) in enumerate(loader_train):
            model.train()  # put model to training mode
            x = x.to(device=device, dtype=dtype)  # move to device, e.g. GPU
            y = y.to(device=device, dtype=dtype)

            scores = model(x)

            loss = F.binary_cross_entropy_with_logits(scores, y.unsqueeze(1))

            optimizer.zero_grad()

            loss.backward()

            optimizer.step()

            if t % print_every == 0:
                plot_x.append(300*e + t)
                plot_y.append(check_accuracy(loader_val, model, False)[0])
                print()

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

print("Training Model")
hidden_layer_size = 64
learning_rate = 0.0005
model = TwoLayerFC(13, hidden_layer_size, 1)
optimizer = optim.Adam(model.parameters(), lr=learning_rate)
train(model, optimizer, epochs=100)

print(check_accuracy(loader_train, model, True))
print(check_accuracy(loader_val, model, False))

plt.plot(plot_x, plot_y)
plt.axis([0,3000,.5,.8])
plt.show()