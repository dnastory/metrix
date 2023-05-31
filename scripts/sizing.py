import os
import csv
import numpy as np

def count_lines_in_file(file_path):
    with open(file_path, 'r') as f:
        for i, _ in enumerate(f):
            pass
    return i + 1

directory = './opensnp'

file_line_counts = {}

for filename in os.listdir(directory):
    if filename.endswith('.vcf'):
        file_path = os.path.join(directory, filename)
        line_count = count_lines_in_file(file_path)
        file_line_counts[filename] = line_count

with open('snp_counts.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['filename', 'snp_count'])
    for filename, line_count in file_line_counts.items():
        writer.writerow([filename, line_count])

counts = np.array(list(file_line_counts.values()))
print(f'Min: {np.min(counts)}')
print(f'Max: {np.max(counts)}')
print(f'Mean: {np.mean(counts)}')
print(f'Variance: {np.var(counts)}')
