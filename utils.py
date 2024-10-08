import numpy as np
import torch
from pandas.core.frame import DataFrame


def try_gpu(i=0):
    if torch.cuda.device_count() >= i + 1:
        return torch.device(f'cuda:{i}')
    else:
        return torch.device('cpu')


def find_amino_acid(x):
    return ('B' in x) | ('O' in x) | ('J' in x) | ('U' in x) | ('X' in x) | ('Z' in x)


def CT(sequence):
    classMap = {'G': '1', 'A': '1', 'V': '1', 'L': '2', 'I': '2', 'F': '2', 'P': '2',
                'Y': '3', 'M': '3', 'T': '3', 'S': '3', 'H': '4', 'N': '4', 'Q': '4', 'W': '4',
                'R': '5', 'K': '5', 'D': '6', 'E': '6', 'C': '7'}

    seq = ''.join([classMap[x] for x in sequence])
    length = len(seq)
    coding = np.zeros(343, dtype=int)
    for i in range(length - 2):
        index = int(seq[i]) + (int(seq[i + 1]) - 1) * 7 + (int(seq[i + 2]) - 1) * 49 - 1
        coding[index] = coding[index] + 1
    return coding


def sequence_CT(gene_entry_seq):
    ambiguous_index = gene_entry_seq.loc[
        gene_entry_seq['Sequence'].apply(find_amino_acid)].index
    gene_entry_seq.drop(ambiguous_index, axis=0, inplace=True)
    gene_entry_seq.index = range(len(gene_entry_seq))
    print("after filtering:", gene_entry_seq.shape)
    print("encode amino acid sequence using CT...")
    CT_list = []
    for seq in gene_entry_seq['Sequence'].values:
        CT_list.append(CT(seq))
    gene_entry_seq['features_seq'] = CT_list
    return gene_entry_seq


def preprocessing_PPI(PPI, Sequence):
    PPI_protein_list = list(set(PPI['protein1'].unique()).union(set(PPI['protein2'].unique())))
    PPI_protein = DataFrame(PPI_protein_list)
    PPI_protein['Entry'] = PPI_protein[0].apply(
        lambda x: Sequence[Sequence['Gene Names'].str.contains(x, case=False, na=False)]['Entry'].values[0] if Sequence[
            'Gene Names'].str.contains(x, case=False).any() else 'NA')
    PPI_protein.columns = ['Gene_symbol', 'Entry']
    PPI_protein = PPI_protein[PPI_protein['Entry'] != 'NA']
    PPI_protein = PPI_protein[PPI_protein['Entry'].isin(set(Sequence['Entry']))]
    PPI_protein_list = list(set(PPI_protein['Gene_symbol'].unique()))
    PPI = PPI[PPI['protein1'].isin(PPI_protein_list)]
    PPI = PPI[PPI['protein2'].isin(PPI_protein_list)]
    PPI_protein_list = list(set(PPI['protein1'].unique()).union(set(PPI['protein2'].unique())))
    PPI_protein = PPI_protein[PPI_protein['Gene_symbol'].isin(PPI_protein_list)]
    PPI_protein = PPI_protein.sort_values(by=['Gene_symbol'])
    PPI_protein_list = list(PPI_protein['Gene_symbol'].unique())
    protein_dict = dict(zip(PPI_protein_list, list(range(0, len(PPI_protein_list)))))
    PPI['protein1'] = PPI['protein1'].apply(lambda x: protein_dict[x])
    PPI['protein2'] = PPI['protein2'].apply(lambda x: protein_dict[x])
    PPI_protein['ID'] = PPI_protein['Gene_symbol'].apply(lambda x: protein_dict[x])
    PPI_protein = PPI_protein.sort_values(by=['ID'])
    return PPI, PPI_protein


def Nested_list_dup(Nested_list):
    Nested_list = [sorted(sublist) for sublist in Nested_list]
    Nested_list_dup = []
    for sublist in Nested_list:
        if sublist not in Nested_list_dup:
            Nested_list_dup.append(sublist)
    return Nested_list_dup


def count_unique_elements(lst):
    unique_elements = set()
    for sub_lst in lst:
        unique_elements |= set(sub_lst)
    return unique_elements
