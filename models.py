from layers import InnerProductDecoder, Attention, HGNNConv
import torch
import torch.nn as nn


class HGNN(nn.Module):
    """The HGNN model proposed in `Hypergraph Neural Networks <https://arxiv.org/pdf/1809.09401>`_ paper (AAAI 2019)."""
    def __init__(
            self,
            in_channels: int,
            hid_channels: int,
            num_classes: int,
            num_hyperedges: int,
            use_bn: bool = False,
            drop_rate: float = 0.5,
    ) -> None:
        super().__init__()
        self.layer1 = HGNNConv(in_channels, hid_channels, use_bn=use_bn, drop_rate=drop_rate)
        self.layer2 = HGNNConv(hid_channels, num_classes, use_bn=use_bn, is_last=True)
        self.layer3 = HGNNConv(hid_channels, num_classes, use_bn=use_bn, is_last=True)
        self.attention = Attention(num_classes, 50)
        self.decoder = InnerProductDecoder(drop_rate, act=lambda x: x)

    def encode(self, x, hg):
        hidden1 = self.layer1(x, hg)
        return self.layer2(hidden1, hg), self.layer3(hidden1, hg)

    def reparameterize(self, mu, logvar):
        if self.training:
            std = torch.exp(logvar)
            eps = torch.randn_like(std)
            return eps.mul(std).add_(mu)
        else:
            return mu

    def forward(self, X, hg):
        """
        Args:
            ``X`` (``torch.Tensor``): Input vertex feature matrix. Size :math:`(N, C_{in})`.
            ``hg`` (``dhgHypergraph``): The hypergraph structure that contains :math:`N` vertices.
        """
        mu, logvar = self.encode(X, hg)
        X = self.reparameterize(mu, logvar)
        Z, edge_w = self.attention(X, hg)
        H = self.decoder(X, Z)
        H = torch.sigmoid(H)
        return X, Z, H, mu, logvar, edge_w

