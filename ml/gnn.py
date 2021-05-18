# -*- coding: utf-8 -*-
"""
## Graph Classifier GNN Training Attempt
The code in this notebook is referenced from the tutorials at https://www.dgl.ai/, 
please refer to Deep Graph Library (Tutorials) section to find out more.
"""

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline

"""## Data Ingest

"""

from dgl.nn.pytorch import GraphConv
import pandas as pd
from torch.utils.data import DataLoader
import torch.optim as optim
import torch.nn.functional as F
import torch.nn as nn
from google.colab import drive
import networkx as nx
import matplotlib.pyplot as plt
import os
import torch
from dgl.data import DGLDataset
import dgl
!pip install "tensorflow>=2.2.0"
!pip install dgl

!pip freeze


# Commented out IPython magic to ensure Python compatibility.
drive.mount('/content/gdrive')

# change to working tensorflow directory on the drive
# %cd '/content/gdrive/My Drive/TF/models'

EDGES_PATH_TRAIN = "/content/gdrive/My Drive/TF/models/research/object_detection/graph_edges.csv"
PROPERTIES_PATH_TRAIN = "/content/gdrive/My Drive/TF/models/research/object_detection/graph_properties.csv"
EDGES_PATH_TEST = "/content/gdrive/My Drive/TF/models/research/object_detection/graph_edges_test.csv"
PROPERTIES_PATH_TEST = "/content/gdrive/My Drive/TF/models/research/object_detection/graph_properties_test.csv"


class SyntheticDataset(DGLDataset):
    csv_edges_path = ""
    csv_propeties_path = ""
    num_classes = 0

    def __init__(self, csv_edges_path, csv_propeties_path, num_classes):
        self.csv_edges_path = csv_edges_path
        self.csv_propeties_path = csv_propeties_path
        self.num_classes = num_classes
        super().__init__(name='synthetic')

    def process(self):
        edges = pd.read_csv(self.csv_edges_path)
        properties = pd.read_csv(self.csv_propeties_path)
        self.graphs = []
        self.labels = []

        label_dict = {}
        num_nodes_dict = {}
        for _, row in properties.iterrows():
            label_dict[row['graph_id']] = row['label']
            num_nodes_dict[row['graph_id']] = row['num_nodes']

        edges_group = edges.groupby('graph_id')

        for graph_id in edges_group.groups:
            edges_of_id = edges_group.get_group(graph_id)
            src = edges_of_id['src'].to_numpy()
            dst = edges_of_id['dst'].to_numpy()
            num_nodes = num_nodes_dict[graph_id]
            label = label_dict[graph_id]

            g = dgl.graph((src, dst), num_nodes=num_nodes)
            self.graphs.append(g)
            self.labels.append(label)

        self.labels = torch.LongTensor(self.labels)

    def __getitem__(self, i):
        return self.graphs[i], self.labels[i]

    def __len__(self):
        return len(self.graphs)


trainset = SyntheticDataset(EDGES_PATH_TRAIN, PROPERTIES_PATH_TRAIN, 2)
testset = SyntheticDataset(EDGES_PATH_TEST, PROPERTIES_PATH_TEST, 2)
graph, label = trainset[0]
print(graph, label)

graph, label = testset[0]
fig, ax = plt.subplots()
nx.draw(graph.to_networkx(), ax=ax)
ax.set_title('Class: {:d}'.format(label))
plt.show()

graph, label = trainset[69]
fig, ax = plt.subplots()
nx.draw(graph.to_networkx(), ax=ax)
ax.set_title('Class: {:d}'.format(label))
plt.show()


def collate(samples):
    graphs, labels = map(list, zip(*samples))
    batched_graph = dgl.batch(graphs)
    return batched_graph, torch.tensor(labels)


class Classifier(nn.Module):
    def __init__(self, in_dim, hidden_dim, n_classes):
        super(Classifier, self).__init__()
        self.conv1 = GraphConv(in_dim, hidden_dim)
        self.conv2 = GraphConv(hidden_dim, hidden_dim)
        self.classify = nn.Linear(hidden_dim, n_classes)

    def forward(self, g):
        h = g.in_degrees().view(-1, 1).float()
        h = F.relu(self.conv1(g, h))
        h = F.relu(self.conv2(g, h))
        g.ndata['h'] = h
        hg = dgl.mean_nodes(g, 'h')
        return self.classify(hg)


"""## Train

"""


data_loader = DataLoader(trainset, batch_size=1, shuffle=True,
                         collate_fn=collate)

model = Classifier(1, 256, trainset.num_classes)
loss_func = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.0001)
model.train()

epoch_losses = []
for epoch in range(200):
    epoch_loss = 0
    for iter, (bg, label) in enumerate(data_loader):
        bg = dgl.add_self_loop(bg)
        prediction = model(bg)
        loss = loss_func(prediction, label)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        epoch_loss += loss.detach().item()
    epoch_loss /= (iter + 1)
    print('Epoch {}, loss {:.4f}'.format(epoch, epoch_loss))
    epoch_losses.append(epoch_loss)

"""## Eval"""

plt.title('cross entropy averaged over minibatches')
plt.plot(epoch_losses)
plt.show()

model.eval()
# Convert a list of tuples to two lists
test_X, test_Y = map(list, zip(*testset))
test_bg = dgl.batch(test_X)
test_Y = torch.tensor(test_Y).float().view(-1, 1)
test_bg = dgl.add_self_loop(test_bg)
probs_Y = torch.softmax(model(test_bg), 1)
sampled_Y = torch.multinomial(probs_Y, 1)
argmax_Y = torch.max(probs_Y, 1)[1].view(-1, 1)
print('Accuracy of sampled predictions on the test set: {:.4f}%'.format(
    (test_Y == sampled_Y.float()).sum().item() / len(test_Y) * 100))
print('Accuracy of argmax predictions on the test set: {:4f}%'.format(
    (test_Y == argmax_Y.float()).sum().item() / len(test_Y) * 100))

torch.save(model.state_dict(), "../models/gcn_model")

test_model = Classifier(1, 256, trainset.num_classes)
test_model.load_state_dict(torch.load("../models/gcn_model"))

graph, label = testset[0]
graph = dgl.add_self_loop(graph)
res = test_model(graph)
probs = torch.softmax(res, 1)
sampled_Y = torch.multinomial(probs, 1)
argmax_Y = torch.max(probs, 1)[1].view(-1, 1)
print(argmax_Y.numpy()[0][0])

test = []
for i in probs.detach().numpy()[0]:
    test.append(i)
print(test)
