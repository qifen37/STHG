STHG
====
This is the code for our paper: Multi-source biological knowledge-guided spatiotemporal subnet construction and hypergraph embedding method for protein complex identification

Installation
------------
The following packages for python 3 are required:  

- torch==1.13.1
- numpy==1.26.2
- dhg==0.9.4
- networkx==3.2.1
- scikit-learn==1.3.0

## Datasets

| Dataset     | Number of Proteins | Number of Edges | Number of Cliques | Average Number of Neighbors |
| ----------- | :----------------- | --------------- | ----------------- | --------------------------- |
| Biogrid     | 5640               | 59748           | 38616             | 21.187                      |
| DIP         | 4928               | 17201           | 7832              | 6.981                       |
| Krogan14K   | 3581               | 14076           | 4075              | 7.861                       |
| Collins     | 1622               | 9074            | 4990              | 11.189                      |
| Krogan-core | 2708               | 7123            | 2681              | 5.261                       |

Usage
------------

- step1: python Get_GO_CC_TT.py
- step2: python construct_subnetwork.py
- step3: python hypergraph_embedding.py
- step4: python {dataset}_Attribute.py
- step5: python {dataset}_Update_Weight.py
- step6: python {dataset}_Cluster_Complex.py
- step7: python {dataset}_remove_dup.py
- step8: python Calculate_Metric.py

