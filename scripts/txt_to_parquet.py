# reference: https://arvkevi.github.io/Out_of_Core_Genomics.html

import dask.dataframe as dd
import os

# specify the data types of your columns
dtype={'#CHROM': 'object', 'POS': 'int64', 'ID': 'object', 'REF': 'object', 
       'ALT': 'object', 'QUAL': 'object', 'FILTER': 'object', 'INFO': 'object', 
       'FORMAT': 'object'}

input_dir = '../../genomeprep/opensnp_txt'
output_dir = '../../genomeprep/opensnp_parquet'

count = 0
for filename in os.listdir(input_dir):
    if filename.endswith('.txt'):
        count += 1
        print("count: ", count)
        sample_name = filename.split('.')[0]
        dtype[sample_name] = 'object'
        print(f"Processing file: {filename}")
        try:
            df = dd.read_csv(os.path.join(input_dir, filename), delimiter = "\t", 
                             comment='#', header=None, names=list(dtype.keys()), dtype=dtype, blocksize=1e6)
            df.to_parquet(os.path.join(output_dir, filename.replace('.txt', '.parquet')), engine='pyarrow')
        except Exception as e:
            print(f"Failed to process file: {filename} with error: {str(e)}")
