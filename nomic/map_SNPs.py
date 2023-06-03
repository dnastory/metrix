from nomic import atlas
import pandas as pd
import numpy as np
import os
import csv
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_config():
    db_config = [os.getenv("DB_NAME"), os.getenv("DB_USER"), os.getenv("DB_PASSWORD")]
    return db_config

db_config = get_db_config()

connection = psycopg2.connect(database=db_config[0], user=db_config[1], password=db_config[2])

try:
    cursor = connection.cursor()
    query = """
            SELECT DISTINCT ON (snpediametadata.rs_id, snpediametadata.gene, snpediametadata.chromosome, snpediametadata.position, snpediametadata.orientation) 
            snpediametadata.rs_id, snpediametadata.gene, snpediametadata.chromosome, 
            snpediametadata.position, snpediametadata.orientation, snpedia_unstructured.llm_summary
            FROM snpediametadata
            INNER JOIN snpedia_unstructured ON snpediametadata.rs_id = snpedia_unstructured.rs_id
        """
    cursor.execute(query)
    rows = cursor.fetchall()

    csv_file = "./snpedia_unstructured.csv"

    if os.path.exists(csv_file):
        os.remove(csv_file)

    try:
        with open(csv_file, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["rs_id", "gene", "chromosome", "position", "orientation", "llm_summary"])
            writer.writerows(rows)
    except Exception as e:
        print(f"An error occurred when writing to {csv_file}:", e)

    cursor.close()
except Exception as e:
    print("An error occurred:", e)
finally:
    connection.close()

csv_length = sum(1 for _ in open(csv_file))
print("Length of file:", csv_length)

data = pd.read_csv(csv_file).fillna('')

data['rs_id'] = data['rs_id'].astype(str)

documents = data.to_dict('records')

print(f'Number of documents: {len(documents)}')

project = atlas.map_text(
    data=documents,
    id_field='rs_id',
    indexed_field='llm_summary',
    name='SNPs_v2',
    description='Single Nucleotide Polymorphisms',
    # reset_project_if_exists=True (this changes the URL anyway)
)
