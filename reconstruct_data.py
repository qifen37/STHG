path = "dataset/Krogan14K/krogan14k.txt"
reconstruct = "dataset/Krogan14K/krogan14k_co.txt"

with open(path) as f:
    for line in f:
        ele = line.strip().split()
        with open(reconstruct, 'a') as r:
            r.write(ele[0] + " " + ele[1] + "\n")
