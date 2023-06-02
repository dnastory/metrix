import subprocess
import psycopg2
import sqlite3
import logging

logging.basicConfig(filename='batch_snpediator.log', level=logging.INFO)

def get_db_config():
    with open('./db_config.txt', 'r') as f:
        db_config = [line.strip() for line in f.readlines()]
        return db_config

def get_unprocessed_snps(cur, sqlite_conn):
    try:
        # Get all SNPs from PostgreSQL
        cur.execute("""
            SELECT lower(snps.rs_id) 
            FROM snps
        """)
        pg_snps = set([row[0] for row in cur.fetchall()])

        print(f'Retrieved {len(pg_snps)} SNPs...')

        # Get all SNPs from SQLite
        sqlite_cur = sqlite_conn.cursor()
        sqlite_cur.execute("""
            SELECT lower(rsid)
            FROM genotypes_db
            UNION ALL
            SELECT lower(rsid)
            FROM columns_db
            UNION ALL
            SELECT lower(rsid)
            FROM not_found_snps_db
        """)
        sqlite_snps = set([row[0] for row in sqlite_cur.fetchall()])

        # Get unprocessed SNPs
        unprocessed_snps = pg_snps.difference(sqlite_snps)

        print(f'{len(unprocessed_snps)} SNPs are unprocessed...')

        return unprocessed_snps
    except Exception as e:
        logging.error(f'Error getting unprocessed SNPs: {e}')

def run_snpediator(rs_id, sqlite_conn):
    command = f'snpediator -r {rs_id}'
    try:
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        if 'rsid not found' in output:
            status = 'not found'
            logging.warning(f'rsid not found for rs_id {rs_id}')
            try:
                sqlite_cur = sqlite_conn.cursor()
                sqlite_cur.execute("""
                    INSERT OR IGNORE INTO not_found_snps_db (rsid, status) VALUES (?, ?)
                """, (rs_id, status))
                sqlite_conn.commit()
            except Exception as e:
                logging.error(f'Error inserting not found SNP {rs_id}: {e}')
        else:
            status = 'successful'
            logging.info(f'Successfully ran snpediator for rs_id {rs_id}')
    except subprocess.CalledProcessError as e:
        print(f'Failed to run snpediator for rs_id {rs_id}. Error: {e}')
        status = 'failed'
        logging.error(f'Failed to run snpediator for rs_id {rs_id}. Error: {e}')

    # Update not_found_snps_db with status
    try:
        sqlite_cur = sqlite_conn.cursor()
        sqlite_cur.execute("""
            INSERT OR IGNORE INTO not_found_snps_db (rsid, status) VALUES (?, ?)
        """, (rs_id, status))
        sqlite_conn.commit()
    except Exception as e:
        logging.error(f'Error updating not_found_snps_db with status for SNP {rs_id}: {e}')

if __name__ == "__main__":
    db_name, db_user, db_password, db_host, db_port = get_db_config()

    try:
        with psycopg2.connect(dbname=db_name,
                            user=db_user,
                            password=db_password,
                            host=db_host,
                            port=db_port) as conn:
            with conn.cursor() as cur:
                with sqlite3.connect('/home/ec2-user/.local/share/snpediator/snpediator_local.db') as sqlite_conn:
                    unprocessed_snps = get_unprocessed_snps(cur, sqlite_conn)
                    for rs_id in unprocessed_snps:
                        run_snpediator(rs_id, sqlite_conn)
    except Exception as e:
        logging.error(f'Unexpected error: {e}')
