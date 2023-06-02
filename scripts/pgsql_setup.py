import os
import psycopg2
import psycopg2.extras
import csv
from datetime import datetime

def get_db_config():
    with open('./db_config.txt', 'r') as f:
        db_config = [line.strip() for line in f.readlines()]
        return db_config

def print_database_sizes(cur):
    cur.execute("SELECT COUNT(*) FROM users")
    print(f"Number of records in users table: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM files")
    print(f"Number of records in files table: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM snps")
    print(f"Number of records in snps table: {cur.fetchone()[0]}")

    cur.execute("SELECT COUNT(*) FROM usersnps")
    print(f"Number of records in usersnps table: {cur.fetchone()[0]}")

def get_or_create_user_id(user_id, sequencing_service, cur):
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

def get_or_create_file_id(user_id, filename, cur):
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

def write_checkpoint(filename, line_number):
    with open('checkpoint.txt', 'w') as f:
        f.write(f'{filename}\n{line_number}')

def read_checkpoint():
    try:
        with open('checkpoint.txt', 'r') as f:
            filename = f.readline().strip()
            line_number = int(f.readline().strip())
            return filename, line_number
    except FileNotFoundError:
        return None, None

def parse_txt(txt_file, user_id, file_id, cur):
    last_checkpoint_filename, last_checkpoint_line = read_checkpoint()
    resume = last_checkpoint_filename is None or last_checkpoint_filename != txt_file

    with open(txt_file, 'r') as f:
        vcf_reader = csv.reader(f, delimiter='\t')

        snp_records = []
        usersnp_records = []

        for i, rec in enumerate(vcf_reader):
            if rec[0].startswith('#') or not resume:
                continue

            if i == last_checkpoint_line:
                resume = True

            snp_records.append((rec[2], rec[0], rec[1], rec[3], rec[4], rec[5], rec[6], rec[7], rec[8]))
            
            genotype = rec[9].replace('(', '').replace(')', '').replace(',','/') 

            usersnp_records.append((user_id, file_id, rec[2], genotype))

            if i % 1000 == 0:  # To adjust for batch insertion
                try:
                    psycopg2.extras.execute_values(
                        cur,
                        """
                        INSERT INTO snps (rs_id, chromosome_number, position, reference, alternate, qual, filter, info, format)
                        VALUES %s
                        ON CONFLICT (rs_id) DO NOTHING
                        """,
                        snp_records
                    )

                    psycopg2.extras.execute_values(
                        cur,
                        """
                        INSERT INTO usersnps (user_id, file_id, rs_id, genotype)
                        VALUES %s
                        ON CONFLICT (user_id, file_id, rs_id) DO NOTHING
                        """,
                        usersnp_records
                    )

                    snp_records.clear()
                    usersnp_records.clear()

                    write_checkpoint(txt_file, i)

                except Exception as e:
                    print(f"Error inserting SNP{rec[2]} from file {txt_file}: {e}\n")
                    conn.rollback()
        conn.commit()



def process_file(filename, vcf_dir, cur):
    if filename.endswith('.txt'):
        _, sequencing_service, user_id, __ = filename.split('.')
        user_id = int(user_id)

        user_id = get_or_create_user_id(user_id, sequencing_service, cur)

        file_id = get_or_create_file_id(user_id, filename, cur)

        parse_txt(os.path.join(vcf_dir, filename), user_id, file_id, cur)

        return True
    return False

def process_files_in_directory(vcf_dir, cur):
    files = os.listdir(vcf_dir)
    file_count = len([f for f in files if f.endswith('.txt')])
    processed_files = 0

    for filename in files:
        if process_file(filename, vcf_dir, cur):
            processed_files += 1
            print(f"Processed {processed_files} out of {file_count} files.")
            print_database_sizes(cur)


if __name__ == "__main__":
    db_name, db_user, db_password, db_host, db_port = get_db_config()

    with psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    ) as conn:
        with conn.cursor() as cur:
            vcf_dir = '../../genomeprep/opensnp_txt'
            process_files_in_directory(vcf_dir, cur)
            conn.commit()

    print("Finished processing files.")
