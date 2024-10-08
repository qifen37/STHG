import numpy as np
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
import os

ppi_path = "biogrid_subnetwork"
embedding_path = "biogrid_subnetwork_embedding"
attr_path = "biogrid_attr"
attr_sim_path = "biogrid_attr_sim"
attr_vector_path = "biogrid_attr_vector"
node_path = "biogrid_node"

for h in os.listdir(ppi_path):
    node_file = h.split('.')[0]
    str1 = f"{attr_vector_path}/{node_file}_attr_vector.txt"
    str2 = f"{attr_sim_path}/{node_file}_attr_sim.txt"
    str3 = f"{ppi_path}/{h}"
    str4 = f"{attr_path}/Attribute_{node_file}.txt"
    str5 = f"{embedding_path}/{node_file}_feature_HGVAE.pt"

    file = torch.load(str5)
    file = file.to('cpu')
    file = file.detach().numpy()
    data = torch.load(str5)
    data = data.to('cpu')
    file = data.detach().numpy()

    attr = np.loadtxt(str4)
    scaler_seq = StandardScaler()
    file = scaler_seq.fit_transform(file)
    scaler_go = StandardScaler()
    go_attr = scaler_go.fit_transform(attr)

    file = np.hstack((file, go_attr))


    class Autoencoder(nn.Module):
        def __init__(self, input_dim, embedding_dim):
            super(Autoencoder, self).__init__()
            self.encoder = nn.Sequential(
                nn.Linear(input_dim, 256),
                nn.ReLU(),
                nn.Linear(256, embedding_dim)
            )
            self.decoder = nn.Sequential(
                nn.Linear(embedding_dim, 256),
                nn.ReLU(),
                nn.Linear(256, input_dim)
            )

        def forward(self, x):
            encoded = self.encoder(x)
            decoded = self.decoder(encoded)
            return encoded, decoded


    autoencoder = Autoencoder(input_dim=file.shape[1], embedding_dim=128)
    optimizer = torch.optim.Adam(autoencoder.parameters(), lr=0.001)
    loss_function = nn.MSELoss()

    fused_features_tensor = torch.tensor(file, dtype=torch.float32)

    for epoch in range(100):
        optimizer.zero_grad()
        encoded, decoded = autoencoder(fused_features_tensor)
        loss = loss_function(decoded, fused_features_tensor)
        loss.backward()
        optimizer.step()

    file = encoded.detach().numpy()

    file1 = open(str3)
    file2 = open(str1, 'w')
    print("get the vector representation: ")
    node = []
    for j in file1:
        temp1 = j.split(' ')[0]
        temp2 = j.split(' ')[1].rstrip('\n')
        if temp1 not in node:
            node.append(temp1)
        if temp2 not in node:
            node.append(temp2)
    file1.close()

    with open(f"{node_path}/{node_file}_node.txt", 'r') as f:
        node = f.readlines()
        for i in range(len(node)):
            s1 = node[i].rstrip('\n')
            file2.write(s1)
            file2.write(' ')
            s2 = str(file[i, :]).replace('[', '')
            s2 = s2.replace(']', '')
            s2 = s2.replace('\n', ' ')
            file2.write(s2)
            file2.write('\n')
        file2.close()

    print("calculate the similarity between two nodes:")
    file = open(str1)
    file1 = open(str3)
    file2 = open(str2, 'w')


    def cos_sim(vector1, vector2):
        dot_product = 0.0
        normA = 0.0
        normB = 0.0
        for a, b in zip(vector1, vector2):
            dot_product += a * b
            normA += a ** 2
            normB += b ** 2
        result = dot_product / ((normA * normB) ** 0.5)
        return result


    edge_name_name = []
    for i in file1:
        node_name1 = i.split(' ')[0]
        node_name2 = i.split(' ')[1]
        node_name2 = node_name2.split('\n')[0]
        d = {'node_name1': node_name1, 'node_name2': node_name2}
        edge_name_name.append(d)

    vector = []
    for i in file:
        if not i.strip(): continue
        node_name = i.split(' ', 1)[0]
        node_vector = i.split(' ', 1)[1].rstrip('\n')
        node_vector = node_vector.split()
        node_vector = list(map(float, node_vector))
        d = {'node_name': node_name, 'node_vector': node_vector}
        vector.append(d)

    v1 = []
    v2 = []
    for i in edge_name_name:
        temp1 = 0
        temp2 = 0
        for j in vector:
            if i['node_name1'] == j['node_name']:
                v1 = np.array(j['node_vector'])
                temp1 = 1
        for z in vector:
            if i['node_name2'] == z['node_name']:
                v2 = np.array(z['node_vector'])
                temp2 = 1
        if (temp1 == 1) and (temp2 == 1):
            result = cos_sim(v1, v2)
            file2.write(i['node_name1'])
            file2.write(' ')
            file2.write(i['node_name2'])
            file2.write(' ')
            file2.write(str(result))
            file2.write('\n')

    file.close()
    file1.close()
    file2.close()
