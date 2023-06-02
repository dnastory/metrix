import subprocess
import psycopg2
import logging

logging.basicConfig(filename='snpediator.log', level=logging.INFO)

def get_db_config():
    with open('./db_config.txt', 'r') as f:
        db_config = [line.strip() for line in f.readlines()]
        return db_config

def create_processed_snps_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS processed_snps (
            rs_id TEXT PRIMARY KEY
        )
    """)

def get_unprocessed_snps(cur):
    cur.execute("""
        SELECT snps.rs_id 
        FROM snps
        LEFT JOIN processed_snps 
        ON snps.rs_id = processed_snps.rs_id
        WHERE processed_snps.rs_id IS NULL
    """)
    snps = cur.fetchall()
    return snps

def mark_snp_as_processed(cur, rs_id):
    cur.execute("""
        INSERT INTO processed_snps (rs_id)
        VALUES (%s)
    """, (rs_id,))

def run_snpediator(rs_id):
    command = f'snpediator -r {rs_id}'
    try:
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        logging.info(f'Successfully ran snpediator for rs_id {rs_id}')
    except subprocess.CalledProcessError as e:
        print(f'Failed to run snpediator for rs_id {rs_id}. Error: {e}')
        logging.error(f'Failed to run snpediator for rs_id {rs_id}. Error: {e}')

if __name__ == "__main__":
    db_name, db_user, db_password, db_host, db_port = get_db_config()

    try:
        with psycopg2.connect(dbname=db_name,
                            user=db_user,
                            password=db_password,
                            host=db_host,
                            port=db_port) as conn:
            with conn.cursor() as cur:
                create_processed_snps_table(cur)
                snps = get_unprocessed_snps(cur)
                for rs_id, in snps:
                    run_snpediator(rs_id)
                    mark_snp_as_processed(cur, rs_id)
    except Exception as e:
        logging.error(f'Unexpected error: {e}')
