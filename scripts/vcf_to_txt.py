import os
import shutil

source_directory = 'opensnp'
destination_directory = 'opensnp_txt'

os.makedirs(destination_directory, exist_ok=True)

for filename in os.listdir(source_directory):
    if filename.endswith('.vcf'):
        source_file_path = os.path.join(source_directory, filename)
        destination_file_path = os.path.join(destination_directory, filename.replace('.vcf', '.txt'))
        
        shutil.copy(source_file_path, destination_file_path)
