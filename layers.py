import torch
import torch.nn as nn
import torch.nn.functional as F
from dhg.structure.hypergraphs import Hypergraph
import utils


class HGNNConv(nn.Module):

    def __init__(
            self,
            in_channels: int,
            out_channels: int,
            bias: bool = True,
            use_bn: bool = False,
            drop_rate: float = 0.5,
            is_last: bool = False,
    ):
        super().__init__()
        self.is_last = is_last
        self.bn = nn.BatchNorm1d(out_channels) if use_bn else None
        self.act = nn.ReLU(inplace=True)
        self.drop = nn.Dropout(drop_rate)
        self.theta = nn.Linear(in_channels, out_channels, bias=bias)

    def forward(self, X: torch.Tensor, hg: Hypergraph) -> torch.Tensor:
        X = self.theta(X)
        if self.bn is not None:
            X = self.bn(X)
        X = hg.smoothing_with_HGNN(X)
        if not self.is_last:
            X = self.drop(self.act(X))
        return X


class InnerProductDecoder(nn.Module):
    def __init__(self, drop_rate, act=torch.sigmoid):
        super(InnerProductDecoder, self).__init__()
        self.drop_rate = drop_rate
        self.act = act

    def forward(self, X, Z):
        X = F.dropout(X, self.drop_rate, training=self.training)
        Z = F.dropout(Z, self.drop_rate, training=self.training)
        H = self.act(torch.mm(X, Z.T))
        return H


class projection(nn.Module):
    def __init__(
            self,
            hidden_channels: int,
            hidden_size: int,
    ):
        super(projection, self).__init__()
        self.linear1 = nn.Linear(hidden_channels, hidden_size)
        self.linear2 = nn.Linear(hidden_size, 1)

    def forward(self, x):
        x = self.linear1(x)
        x = F.leaky_relu(x)
        x = self.linear2(x)
        return x


class Attention(nn.Module):
    def __init__(
            self,
            hidden_channels: int,
            hidden_size: int,
    ):
        super(Attention, self).__init__()
        self.projection = projection(hidden_channels, hidden_size)

    def forward(self, X, hg):
        global Z
        he = hg.state_dict['raw_groups']['main']
        edges = list(he.keys())
        edge_w = []
        for i in range(len(edges)):
            index = torch.tensor(list(edges[i][0]))
            index = index.to(device=utils.try_gpu())
            x_he = torch.index_select(X, 0, index)
            w = self.projection(x_he)
            beta = torch.softmax(w, dim=0)
            edge_w.append(beta)
            z_batch = (beta * x_he).sum(0)
            z_batch = F.leaky_relu(z_batch)
            z_batch = z_batch.unsqueeze(0)
            if i > 0:
                Z = torch.cat([Z, z_batch], 0)
            else:
                Z = z_batch
        return torch.tanh(Z), edge_w


def loss_function(preds, labels, mu, logvar, n_nodes, norm, pos_weight):
    cost = norm * F.binary_cross_entropy(preds, labels)

    KLD = -0.5 / n_nodes * torch.mean(torch.sum(
        1 + 2 * logvar - mu.pow(2) - logvar.exp().pow(2), 1))
    return cost + KLD
