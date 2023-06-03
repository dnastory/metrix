import psycopg2
import sqlite3
import logging
import sys
import time
import locale

def format_number_with_commas(number):
    locale.setlocale(locale.LC_ALL, 'en_US')

    formatted_number = locale.format_string("%d", number, grouping=True)
    return formatted_number

# unrelated debugging things, just 'cause it's convenient to have here
def count_snpediametadata(cur_pg):
    cur_pg.execute("SELECT COUNT(*) FROM users;")
    count = cur_pg.fetchone()[0]
    print(f'Count of users: {format_number_with_commas(count)}')

    cur_pg.execute("SELECT COUNT(*) FROM snps;")
    count = cur_pg.fetchone()[0]
    print(f'Count of snps: {format_number_with_commas(count)}')

    cur_pg.execute("SELECT COUNT(*) FROM snpediametadata;")
    count = cur_pg.fetchone()[0]
    print(f'Count of snpediametadata: {format_number_with_commas(count)}')

    cur_pg.execute("SELECT COUNT(*) FROM observedphenotypes;")
    count = cur_pg.fetchone()[0]
    print(f'Count of observedphenotypes: {format_number_with_commas(count)}')

    cur_pg.execute("SELECT COUNT(*) FROM usersnps;")
    count = cur_pg.fetchone()[0]
    print(f'Count of usersnps: {format_number_with_commas(count)}')

logging.basicConfig(filename='batch_snpedia.log', level=logging.INFO)


def get_db_config():
    with open('./db_config.txt', 'r') as f:
        db_config = [line.strip() for line in f.readlines()]
        return db_config


def batch_update(cur_pg, data_batch):
    try:
        update_sql = """
        INSERT INTO snpediametadata(id, rs_id, gene, "position", orientation, reference, genotype, magnitude, color, summary, chromosome) 
        VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
        """
        cur_pg.executemany(update_sql, data_batch)
    except Exception as e:
        cur_pg.execute("ROLLBACK")
        logging.error(f'Error updating PostgreSQL: {e}')
        raise e


def process_snpedia_data():
    db_config = get_db_config()
    conn_pg = psycopg2.connect(database=db_config[0], user=db_config[1], password=db_config[2])
    cur_pg = conn_pg.cursor()

    conn_sqlite = sqlite3.connect('/home/ec2-user/.local/share/snpediator/snpediator_local.db')
    cur_sqlite = conn_sqlite.cursor()

    logging.info('SQLite connection status: ' + ('open' if conn_sqlite else 'closed'))

    logging.info('Fetching rs_ids from PostgreSQL...')
    cur_pg.execute("SELECT rs_id FROM snpediametadata;")
    pg_rs_ids = {rs_id[0].upper() for rs_id in cur_pg.fetchall()}  # PostgreSQL rs_ids

    logging.info('Fetching rs_ids from SQLite3...')
    cur_sqlite.execute("SELECT DISTINCT rsid FROM genotypes_db;")
    sqlite_rs_ids = {rs_id[0] for rs_id in cur_sqlite.fetchall()}  # SQLite3 rs_ids

    unprocessed_rs_ids = sqlite_rs_ids.difference(pg_rs_ids)  # rs_ids in SQLite but not in PostgreSQL
    logging.info(f'Unprocessed rs_ids count: {len(unprocessed_rs_ids)}')

    batch_size = 10
    data_batch = []
    for rs_id in unprocessed_rs_ids:
        rs_id_pg = rs_id.lower()  # PostgreSQL rs_id

        logging.info(f'Fetching columns_db record for {rs_id}...')
        cur_sqlite.execute("SELECT * FROM columns_db WHERE rsid = ?", (rs_id,))
        rs_id_columns = cur_sqlite.fetchone()
        logging.info(f'columns_db record for {rs_id}: {rs_id_columns}')

        logging.info(f'Fetching genotypes_db records for {rs_id}...')
        cur_sqlite.execute("SELECT * FROM genotypes_db WHERE rsid = ?", (rs_id,))
        rs_id_genotypes = cur_sqlite.fetchall()
        logging.info(f'genotypes_db records for {rs_id}: {rs_id_genotypes}')

        if rs_id_columns and rs_id_genotypes:
            for rs_id_genotype in rs_id_genotypes:
                rs_id_data = (rs_id_pg, rs_id_columns[1], rs_id_columns[3], rs_id_columns[4], rs_id_columns[5], rs_id_genotype[2], rs_id_genotype[3], rs_id_genotype[4], rs_id_genotype[5], rs_id_columns[2])
                data_batch.append(rs_id_data)

            if len(data_batch) >= batch_size:
                logging.info('Batch size reached. Updating PostgreSQL.')
                try:
                    batch_update(cur_pg, data_batch)
                    conn_pg.commit()
                    logging.info(f'Successfully updated PostgreSQL with {len(data_batch)} records.')
                    data_batch = []
                except Exception as e:
                    logging.error(f'Error updating PostgreSQL: {e}')
                    sys.exit(1)


    if data_batch:  # process remaining records
        logging.info(f'Updating PostgreSQL with remaining records.')
        try:
            batch_update(cur_pg, data_batch)
            conn_pg.commit()
            logging.info(f'Successfully updated PostgreSQL with {len(data_batch)} records.')
        except Exception as e:
            logging.error(f'Error updating PostgreSQL: {e}')

    count_snpediametadata(cur_pg)

    cur_pg.close()
    conn_pg.close()
    cur_sqlite.close()
    conn_sqlite.close()


if __name__ == "__main__":
    while True:
        process_snpedia_data()
        time.sleep(1800)  # sleep for half an hour
