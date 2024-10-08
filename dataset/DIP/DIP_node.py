import os


folder_path = "DIP_subnetwork"
for h in os.listdir(folder_path):
    node_file = h.split('.')[0]
    protein_dataset = f"{folder_path}/{h}"
    dip_node = open(f"DIP_node/{node_file}_node.txt", 'w')

    node = []

    with open(protein_dataset, 'r') as f:
        for p in f:
            protein1 = p.split()[0]
            protein2 = p.split()[1].rstrip('\n')
            if protein1 not in node:
                node.append(protein1)
                dip_node.write(protein1)
                dip_node.write('\n')
            if protein2 not in node:
                node.append(protein2)
                dip_node.write(protein2)
                dip_node.write('\n')
    dip_node.close()
    print(node)
