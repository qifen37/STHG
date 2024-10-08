import torch.optim as optim
from dhg import Hypergraph
from models import HGNN
import time
from utils import *
from layers import loss_function
from utils import count_unique_elements
import networkx as nx
import pandas as pd
import numpy as np
import torch
from pandas.core.frame import DataFrame


folder_path = "dataset/Biogrid/biogrid_co.txt"

Sequence_path = "knowledge/uniprot-sequences-2023.05.10-01.31.31.11.tsv"
Sequence = pd.read_csv(Sequence_path, sep='\t')
Sequence_feature = sequence_CT(Sequence)

PPI = f"{folder_path}"
PPI = pd.read_csv(PPI, sep=" ", header=None)
PPI.columns = ['protein1', 'protein2']
PPI_trans = PPI[['protein1', 'protein2']].copy()
PPI = pd.concat([PPI, PPI_trans], axis=0).reset_index(drop=True)
PPI, Protein_dict = preprocessing_PPI(PPI, Sequence_feature)
PPI_list = PPI.values.tolist()
PPI_list = Nested_list_dup(PPI_list)

G = nx.Graph()
G.add_edges_from(PPI_list)
PPI_hyperedge_dup = list(nx.find_cliques(G))
unique_elements = count_unique_elements(PPI_hyperedge_dup)
edge_list_data = {"num_vertices": len(unique_elements), "PPI_edge_list": PPI_list, "PPI_cliques_list": PPI_hyperedge_dup}

Sequence_feature = pd.merge(Protein_dict, Sequence_feature, how='inner')
Sequence_feature = Sequence_feature.sort_values(by=['ID'])
Sequence_feature = DataFrame(Sequence_feature['features_seq'].to_list())
X = torch.FloatTensor(np.array(Sequence_feature))
X = X.to(device=try_gpu())

G = Hypergraph(edge_list_data["num_vertices"], edge_list_data["PPI_cliques_list"])
G = G.to(device=try_gpu())
he = G.state_dict['raw_groups']['main']
edges = list(he.keys())
H_incidence = G.H.to_dense()
pos_weight = float(H_incidence.shape[0] * H_incidence.shape[0] - H_incidence.sum()) / H_incidence.sum()
norm = H_incidence.shape[0] * H_incidence.shape[0] / float((H_incidence.shape[0] * H_incidence.shape[0] - H_incidence.sum()) * 2)
net = HGNN(X.shape[1], 200, 100, len(edges), use_bn=True, drop_rate=0.5)
net = net.to(device=try_gpu())
optimizer = optim.Adam(net.parameters(), lr=0.001, weight_decay=5e-4)
list_loss = []
list_epoch = []
total_params = sum(p.numel() for p in net.parameters() if p.requires_grad)
print("Total number of parameters:", total_params)

for epoch in range(500):
    list_epoch.append(epoch)
    net.train()
    st = time.time()
    optimizer.zero_grad()
    recovered, Z, H, mu, logvar, edge_w = net(X, G)
    loss = loss_function(preds=H, labels=G.H.to_dense(),
                         mu=mu, logvar=logvar, n_nodes=edge_list_data["num_vertices"],
                         norm=norm, pos_weight=pos_weight)
    loss.backward()
    optimizer.step()
    list_loss.append(loss.item())
    if epoch % 100 == 0:
        print(f"Epoch: {epoch}, Time: {time.time() - st:.5f}s, Loss: {loss.item():.5f}")
net.eval()
recovered, Z, H, mu, logvar, edge_w = net(X, G)
Embedding = recovered

Embedding_path = f"dataset/Biogrid/biogrid_subnetwork_embedding/biogrid_feature_HGVAE.pt"
torch.save(Embedding, Embedding_path)
print("Finally!")

