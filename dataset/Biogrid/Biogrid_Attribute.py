import re
import os


folder_path = "biogrid_subnetwork"
for h in os.listdir(folder_path):
    node_file = h.split('.')[0]
    str1 = f"{folder_path}/{h}"
    str2 = f"biogrid_attr/Attribute_{node_file}.txt"
    file1 = open(str1)
    node = []
    for j in file1:
        temp1 = j.split()[0]
        temp2 = j.split()[1].rstrip('\n')
        if temp1 not in node:
            node.append(temp1)
        if temp2 not in node:
            node.append(temp2)
    file1.close()

    print("create attributed network!")
    go = []
    file = open("biogrid_go_information.txt")
    file4 = open("biogrid_go_information_temp.txt", 'w')
    for i in file:
        node_name = i.split(' ', 1)[0]
        node_go = i.split(' ', 1)[1].rstrip('\n').rstrip(' ')
        file4.write(node_name)
        file4.write(' ')
        node_go = re.split(" |:", node_go)
        for j in node_go:
            if j != 'GO':
                file4.write(j)
                file4.write(' ')
        file4.write('\n')
        for j in node_go:
            if j not in go:
                go.append(j)
    file.close()
    file4.close()
    go.remove('GO')
    go.sort()

    file = open("biogrid_go_information_temp.txt")
    gov = []
    for i in file:
        node_name = i.split(' ', 1)[0]
        node_go = i.split(' ', 1)[1].rstrip('\n').rstrip(' ')
        node_go = node_go.split(' ')
        one = {'node_name': node_name, 'node_go': node_go}
        gov.append(one)
    file.close()

    attr = [[0 for col in range(len(go))] for row in range(len(node))]

    for i in node:
        for j in gov:
            if i == j['node_name']:
                a = node.index(i)
                for z in j['node_go']:
                    for q in go:
                        if z == q:
                            b = go.index(q)
                            attr[a][b] = attr[a][b] + 1

    file3 = open(str2, 'w')
    for i in range(len(node)):
        for j in range(len(go)):
            file3.write(str(attr[i][j]))
            file3.write(' ')
        file3.write('\n')
    file3.close()
    print('success!')
