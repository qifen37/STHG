or_file = "collins_final_result"

final_file = "collins_remove_final_result"
sorted_lines = []
with open(or_file, 'r') as o:
    for lin in o:
        sorted_line = ' '.join(sorted(lin.split()))
        sorted_lines.append(sorted_line)

set_lines = set(sorted_lines)
final_lines = list(set_lines)
with open(final_file, 'w') as f:
    for so_li in final_lines:
        f.write(so_li + "\n")


