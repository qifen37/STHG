Dic_map = {}
index = 0
go_set_list = []
expression_list = []
neighbor_list = []
protein_time_list = []
time_protein_list = []
neighbor_PPI_list = []
Time_num = 12
protein_out_file = "protein.temp"
PPI_file = "dataset/Biogrid/biogrid_co.txt"

# input high-throughput PPI data
f = open(PPI_file, "r")
f_protein_out = open(protein_out_file, "w")
for line in f:
    line = line.strip().split()
    if len(line) == 2:
        if line[0] not in Dic_map:
            Dic_map[line[0]] = index
            f_protein_out.write(line[0] + "\n")
            index += 1
            go_set_list.append(set([]))
            expression_list.append([])
            neighbor_list.append(set([]))
            neighbor_PPI_list.append(set([]))
            protein_time_list.append(set([]))
        if line[1] not in Dic_map:
            Dic_map[line[1]] = index
            f_protein_out.write(line[1] + "\n")
            index += 1
            go_set_list.append(set([]))
            expression_list.append([])
            neighbor_list.append(set([]))
            neighbor_PPI_list.append(set([]))
            protein_time_list.append(set([]))
Protein_num = index
f.close()
f_protein_out.close()

# input Gene expression data
f = open("dataset/series_matrix.txt", "r")
for line in f:
    line = line.strip().split()
    if len(line) == 38:
        if line[1] in Dic_map:
            for i in range(2, Time_num + 2):
                expression_list[Dic_map[line[1]]].append(
                    (float(line[i]) + float(line[i + 12]) + float(line[i + 24])) / 3)
f.close()

# compute active time attribute for proteins
for t in range(0, Time_num):
    time_protein_list.append(set([]))
for instance in Dic_map:
    if len(expression_list[Dic_map[instance]]) >= 12:
        Temp_mean_value = 0.
        Temp_sd_value = 0.
        Temp_thresh_3SD = 0.
        Temp_thresh_2SD = 0.
        Temp_thresh_1SD = 0.
        for j in range(0, Time_num):
            Temp_mean_value += expression_list[Dic_map[instance]][j]
        Temp_mean_value /= Time_num
        for j in range(0, Time_num):
            Temp_sd_value += (expression_list[Dic_map[instance]][j] - Temp_mean_value) ** 2
        Temp_sd_value /= (Time_num - 1)
        k = 1
        Temp_thresh_kSD = Temp_mean_value + k * (Temp_sd_value ** 0.5) * (Temp_sd_value / (1 + Temp_sd_value))
        for j in range(0, Time_num):
            if expression_list[Dic_map[instance]][j] >= Temp_thresh_kSD:
                protein_time_list[Dic_map[instance]].add(j)
                time_protein_list[j].add(Dic_map[instance])

protein_dataset = "dataset/Biogrid/biogrid_co.txt"
dip_node = open("dataset/Biogrid/biogrid_node.txt", 'w')

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

file2 = open("dataset/Biogrid/biogrid_node.txt")
file3 = open("dataset/Biogrid/biogrid_go_information.txt", "w")

for i in file2:
    i = i.rstrip('\n')
    print(i)
    file3.write(i)
    file3.write(' ')
    file1 = open("dataset/go_slim_mapping.tab.txt")
    for j in file1:
        node_name = j.split('	')[0]
        go_tag = j.split('	')[3]
        go = j.split('	')[5]
        if node_name == i:
            if go_tag == "P" or go_tag == 'C' or go_tag == 'F':
                if go != '':
                    file3.write(go)
                    file3.write(' ')
    file1.close()
    file3.write('\n')

file2.close()
file3.close()

file1 = open("dataset/Biogrid/biogrid_go_information.txt")
file2 = open("dataset/Biogrid/biogrid_go_cc_information.txt", 'w')
for i in file1:
    i = i.rstrip('\n')
    file2.write(i)
    file2.write(' ')
    p = i.split()[0]
    file3 = open("dataset/go_slim_mapping.tab.txt")
    for j in file3:
        cfp = j.split('  ')[0].split('\t')
        node_name_1 = cfp[0]
        go_tag_1 = cfp[3]
        if node_name_1 == p:
            if go_tag_1 == "C":
                file2.write(f"CC:{cfp[4]}")
                file2.write(' ')
    file3.close()
    file2.write('\n')
file1.close()
file2.close()

filec = open("dataset/Biogrd/biogrid_go_cc_information.txt")
filect = open("dataset/Biogrid/biogrid_go_cc_tt_information.txt", 'w')
for line in filec:
    line = line.rstrip('\n')
    filect.write(line)
    filect.write(' ')
    pp = line.split()[0]
    for instance in Dic_map:
        if instance == pp:
            print(str(protein_time_list[Dic_map[instance]]))
            filect.write(f"TT:{str(protein_time_list[Dic_map[instance]])}")
            filect.write(' ')
    filect.write('\n')
filec.close()
filect.close()
