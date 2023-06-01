import os
import psycopg2
import csv
from datetime import datetime

with open('./db_config.txt', 'r') as f:
    db_config = [line.strip() for line in f.readlines()]
    db_name, db_user, db_password, db_host, db_port = db_config

conn = psycopg2.connect(
    dbname=db_name,
    user=db_user,
    password=db_password,
    host=db_host,
    port=db_port
)

cur = conn.cursor()

def print_database_sizes():
    cur.execute("SELECT COUNT(*) FROM users")
    print(f"Number of records in users table: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM files")
    print(f"Number of records in files table: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM snps")
    print(f"Number of records in snps table: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM usersnps")
    print(f"Number of records in usersnps table: {cur.fetchone()[0]}")

def get_or_create_user_id(user_id, sequencing_service):
    """
    Get the ID of the user if it exists, otherwise create a new user and return its ID.

    :param user_id: The user_id of the user.
    :return: The ID of the user.
    """
    cur.execute(
        """
        SELECT user_id FROM users WHERE user_id = %s
        """,
        (user_id,)
    )
    result = cur.fetchone()
    if result is None:
        cur.execute(
            """
            INSERT INTO users (user_id, sequencing_service) VALUES (%s, %s)
            RETURNING user_id
            """,
            (user_id, sequencing_service)
        )
        result = cur.fetchone()

    return result[0]

def get_or_create_file_id(user_id, filename):
    """
    Get the ID of the file if it exists, otherwise create a new file and return its ID.

    :param filename: The filename of the file.
    :param user_id: The user_id of the user who uploaded the file.
    :return: The ID of the file.
    """
    cur.execute(
        """
        SELECT file_id FROM files WHERE filename = %s
        """,
        (filename,)
    )
    result = cur.fetchone()
    if result is None:
        cur.execute(
            """
            INSERT INTO files (user_id, filename, file_date) VALUES (%s, %s, %s)
            RETURNING file_id
            """,
            (user_id, filename, datetime.now())
        )
        result = cur.fetchone()

    return result[0]

def parse_txt(txt_file, user_id, file_id):
    """
    Parse a txt file and insert the data into the database.

    :param txt_file: The path to the txt file.
    :param user_id: The user ID.
    :param file_id: The file ID.
    """
    with open(txt_file, 'r') as f:
        vcf_reader = csv.reader(f, delimiter='\t')

        for i, rec in enumerate(vcf_reader):
            if rec[0].startswith('#'):
                continue

            try:
                with conn:
                    with conn.cursor() as curs:
                        # Insert the SNP into the SNPs table
                        curs.execute(
                            """
                            INSERT INTO snps (rs_id, chromosome_number, position, reference, alternate, qual, filter, info, format)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT DO NOTHING
                            """,
                            (rec[2], rec[0], rec[1], rec[3], rec[4], rec[5], rec[6], rec[7], rec[8])
                        )

                        # Insert the UserSNP into the UserSNPs table
                        curs.execute(
                            """
                            INSERT INTO usersnps (user_id, file_id, rs_id, genotype)
                            VALUES (%s, %s, %s, %s)
                            """,
                            (user_id, file_id, rec[2], rec[9])
                        )

            except Exception as e:
                print(f"Error inserting SNP {rec[2]} from file {txt_file}: {e}\n")

def process_file(filename, vcf_dir):
    if filename.endswith('.txt'):
        _, sequencing_service, user_id, __ = filename.split('.')
        user_id = int(user_id)

        user_id = get_or_create_user_id(user_id, sequencing_service)

        file_id = get_or_create_file_id(user_id, filename)

        parse_txt(os.path.join(vcf_dir, filename), user_id, file_id)

        return True
    return False

vcf_dir = '../../genomeprep/opensnp_txt'
files = os.listdir(vcf_dir)
file_count = len([f for f in files if f.endswith('.txt')])
processed_files = 0

for filename in files:
    if process_file(filename, vcf_dir):
        processed_files += 1
        if processed_files % 1 == 0:
            print(f"Processed {processed_files} out of {file_count} files.")
            print_database_sizes()

cur.close()
conn.close()