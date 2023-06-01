import subprocess
import psycopg2
import logging

logging.basicConfig(filename='snpediator.log', level=logging.INFO)

def get_db_config():
    with open('./db_config.txt', 'r') as f:
        db_config = [line.strip() for line in f.readlines()]
        return db_config

def get_snps(cur):
    cur.execute("SELECT rs_id FROM snps")
    snps = cur.fetchall()
    return snps

def write_checkpoint(rs_id):
    with open('snpediator_checkpoint.txt', 'w') as f:
        f.write(rs_id)

def read_checkpoint():
    try:
        with open('snpediator_checkpoint.txt', 'r') as f:
            rs_id = f.readline().strip()
            return rs_id
    except FileNotFoundError:
        return None

def run_snpediator(rs_id):
    command = f'snpediator -r {rs_id}'
    try:
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        logging.info(f'Successfully ran snpediator for rs_id {rs_id}')
        write_checkpoint(rs_id)
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
                snps = get_snps(cur)
                last_processed_snp = read_checkpoint()
                start_from_checkpoint = last_processed_snp is not None

                for rs_id, in snps:
                    if start_from_checkpoint and rs_id != last_processed_snp:
                        continue
                    start_from_checkpoint = False
                    run_snpediator(rs_id)
    except Exception as e:
        logging.error(f'Unexpected error: {e}')
