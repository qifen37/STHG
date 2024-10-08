str = "dataset/Biogrid/biogrid_remove_final_result"
file = open(str)
file1 = open("dataset/golden_standard.txt")

predicted_num = len(file.readlines())
reference_num = len(file1.readlines())
file.close()
file1.close()

file = open(str)
file1 = open("dataset/golden_standard.txt")
reference_complex = []
for j in file1:
    j = j.rstrip()
    j = j.rstrip('\n')
    complex_list = j.split(' ')
    reference_complex.append(complex_list)

predicted_complex = []
for i in file:
    i = i.rstrip()
    i = i.rstrip('\n')
    node_list = i.split(' ')
    predicted_complex.append(node_list)

number = 0
c_number = 0
row = 1
mismatched = []
for i in predicted_complex:
    overlapscore = 0.0
    for j in reference_complex:
        set1 = set(i)
        set2 = set(j)
        overlap = set1 & set2
        score = float((pow(len(overlap), 2))) / float((len(set1) * len(set2)))
        if score > overlapscore:
            overlapscore = score
    if overlapscore > 0.2:
        number = number + 1
        print(row),
        print(" "),
    row = row + 1

# recall
for i in reference_complex:
    overlapscore = 0.0
    for j in predicted_complex:
        set1 = set(i)
        set2 = set(j)
        overlap = set1 & set2
        score = float((pow(len(overlap), 2))) / float((len(set1) * len(set2)))
        if score > overlapscore:
            overlapscore = score
    if overlapscore > 0.25:
        c_number = c_number + 1

# sn
T_sum1 = 0.0
N_sum = 0.0
for i in reference_complex:
    max = 0.0
    for j in predicted_complex:
        set1 = set(i)
        set2 = set(j)
        overlap = set1 & set2
        if len(overlap) > max:
            max = len(overlap)
    T_sum1 = T_sum1 + max
    N_sum = N_sum + len(set1)

# ppv
T_sum2 = 0.0
T_sum = 0.0
for i in predicted_complex:
    max = 0.0
    for j in reference_complex:
        set1 = set(i)
        set2 = set(j)
        overlap = set1 & set2
        T_sum = T_sum + len(overlap)
        if len(overlap) > max:
            max = len(overlap)
    T_sum2 = T_sum2 + max

print(number, predicted_num)
precision = float(number / float(predicted_num))
recall = float(c_number / float(reference_num))
F1 = float((2 * precision * recall) / (precision + recall))
Sn = float(T_sum1) / float(N_sum)
PPV = float(T_sum2) / float(T_sum)
Acc = pow(float(Sn * PPV), 0.5)
print("precision")
print(precision)
print("recall")
print(recall)
print("F1")
print(F1)
print("Acc")
print(Acc)
print("Sn")
print(Sn)
print("PPV")
print(PPV)
file.close()
file1.close()
