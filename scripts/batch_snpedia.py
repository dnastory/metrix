import sqlite3
import psycopg2
import logging
from psycopg2 import sql

logging.basicConfig(filename='batch_snpedia.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

def batch_update(cur, batch):
    insert = sql.SQL(''' 
        INSERT INTO snpediametadata 
        (rs_id, gene, "position", orientation, reference, magnitude, color, summary, chromosome, genotype) 
        VALUES {} 
        ON CONFLICT (rs_id) DO UPDATE SET
        gene = EXCLUDED.gene,
        "position" = EXCLUDED."position",
        orientation = EXCLUDED.orientation,
        reference = EXCLUDED.reference,
        magnitude = EXCLUDED.magnitude,
        color = EXCLUDED.color,
        summary = EXCLUDED.summary,
        chromosome = EXCLUDED.chromosome,
        genotype = EXCLUDED.genotype
        ''').format(sql.SQL(',').join(map(sql.Literal, batch)))
    cur.execute(insert)

def process_snpedia_data():
    conn_pg = psycopg2.connect(database="snp_database", user="olivia", password="olivia")
    cur_pg = conn_pg.cursor()

    conn_sqlite = sqlite3.connect('/home/ec2-user/.local/share/snpediator/snpediator_local.db')
    cur_sqlite = conn_sqlite.cursor()

    logging.info('SQLite connection status: ' + ('open' if conn_sqlite else 'closed'))

    logging.info('Fetching unprocessed snps...')
    cur_pg.execute("""
        SELECT snps.rs_id 
        FROM snps
        LEFT JOIN processed_snps 
        ON snps.rs_id = processed_snps.rs_id
        WHERE processed_snps.rs_id IS NULL
    """)
    snps = cur_pg.fetchall()
    logging.info(f'{len(snps)} unprocessed SNPs fetched.')

    rs_id_columns_batch = []
    batch_size = 5000

    for snp in snps:
        rs_id = snp[0].lower()
        rs_id_sqlite = rs_id.capitalize()  # Convert to SQLite format

        try:
            cur_sqlite.execute("SELECT * FROM columns_db WHERE rsid = ?", (rs_id_sqlite,))
            rs_id_columns = cur_sqlite.fetchone()
        except Exception as e:
            logging.error(f'Error fetching from columns_db for {rs_id_sqlite}: {e}')
            rs_id_columns = None

        try:
            cur_sqlite.execute("SELECT * FROM genotypes_db WHERE rsid = ?", (rs_id_sqlite,))
            rs_id_genotypes = cur_sqlite.fetchall()
        except Exception as e:
            logging.error(f'Error fetching from genotypes_db for {rs_id_sqlite}: {e}')
            rs_id_genotypes = None

        logging.info(f'columns_db record for {rs_id_sqlite}: {rs_id_columns}')
        logging.info(f'genotypes_db records for {rs_id_sqlite}: {rs_id_genotypes}')

        if rs_id_columns and rs_id_genotypes:
            rs_id_genotype = ''.join([genotype[2] for genotype in rs_id_genotypes])
            rs_id_data = (rs_id,) + rs_id_columns[1:] + (rs_id_genotype,)
            rs_id_columns_batch.append(rs_id_data)

            if len(rs_id_columns_batch) >= batch_size:
                logging.info(f'Batch size reached. Updating PostgreSQL.')
                try:
                    batch_update(cur_pg, rs_id_columns_batch)
                    conn_pg.commit()
                    rs_id_columns_batch.clear()
                except Exception as e:
                    logging.error(f'Error updating PostgreSQL for batch: {e}')
        else:
            logging.warning(f'No matching SQLite records for {rs_id_sqlite}. Skipping...')

        try:
            cur_pg.execute("INSERT INTO processed_snps (rs_id) VALUES (%s)", (rs_id,))
            conn_pg.commit()
        except Exception as e:
            logging.error(f'Error updating processed_snps for {rs_id}: {e}')

    if rs_id_columns_batch:
        logging.info(f'Final batch. Updating PostgreSQL.')
        try:
            batch_update(cur_pg, rs_id_columns_batch)
            conn_pg.commit()
        except Exception as e:
            logging.error(f'Error updating PostgreSQL for final batch: {e}')

    cur_pg.close()
    cur_sqlite.close()
    conn_pg.close()
    conn_sqlite.close()


if __name__ == '__main__':
    process_snpedia_data()
