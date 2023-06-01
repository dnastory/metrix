def determine_delimiter(filepath):
    delimiters = [',', '\t', ';']

    delimiter_count = {}
    with open(filepath, 'r') as file:
        for line in file:
            for delimiter in delimiters:
                if delimiter in line:
                    delimiter_count[delimiter] = delimiter_count.get(delimiter, 0) + 1

    return delimiter_count

file_path = '../../genomeprep/opensnp_txt/2406.23andme.1498.txt'
delimiter_counts = determine_delimiter(file_path)
if delimiter_counts:
    print("Delimiter Counts:")
    for delimiter, count in delimiter_counts.items():
        print(f"{delimiter}: {count}")
else:
    print(f"No delimiter found in {file_path}")
