import os
import psycopg2
import pysam
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

def parse_vcf(vcf_file, user_id, file_id):
    """
    Parse a VCF file and insert the data into the database.

    :param vcf_file: The path to the VCF file.
    :param user_id: The user ID.
    :param file_id: The file ID.
    """
    vcf_reader = pysam.VariantFile(vcf_file)

    for i, rec in enumerate(vcf_reader.fetch()):
        try:
            # Insert the SNP into the SNPs table
            cur.execute(
                """
                INSERT INTO snps (rs_id, chromosome_number, position, reference, alternate, qual, filter, info, format)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """,
                (rec.id, rec.chrom, rec.pos, rec.ref, ','.join(rec.alts), rec.qual, ','.join(rec.filter.keys()), str(rec.info), rec.format)
            )

            # Insert the UserSNP into the UserSNPs table
            for sample in rec.samples:
                cur.execute(
                    """
                    INSERT INTO usersnps (user_id, file_id, rs_id, genotype)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user_id, file_id, rec.id, rec.samples[sample]['GT'])
                )
        except Exception as e:
            with open('error_log.txt', 'a') as f:
                f.write(f"Error inserting SNP {rec.id} from file {vcf_file}: {e}\n")

        if i % 1000 == 0:
            conn.commit()

    conn.commit()

vcf_dir = '../../genomeprep/opensnp'

for filename in os.listdir(vcf_dir):
    if filename.endswith('.vcf'):
        _, sequencing_service, user_id, __ = filename.split('.')
        user_id = int(user_id)

        user_id = get_or_create_user_id(user_id, sequencing_service)

        file_id = get_or_create_file_id(user_id, filename)

        parse_vcf(os.path.join(vcf_dir, filename), user_id, file_id)


cur.close()
conn.close()