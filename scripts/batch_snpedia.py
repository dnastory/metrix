import sqlite3
import psycopg2
from psycopg2 import sql

with open('./db_config.txt', 'r') as f:
    db_config = [line.strip() for line in f.readlines()]
    db_name, db_user, db_password, db_host, db_port = db_config


conn_pg = None
conn_sqlite = None

def read_checkpoint():
    try:
        with open('snpedia_checkpoint.txt', 'r') as f:
            rs_id = f.readline().strip()
            return rs_id
    except FileNotFoundError:
        return None

def write_checkpoint(rs_id):
    with open('snpedia_checkpoint.txt', 'w') as f:
        f.write(f'{rs_id}\n')

try:
    conn_pg = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    cur_pg = conn_pg.cursor()

    conn_sqlite = sqlite3.connect('/home/ec2-user/.local/share/snpediator/snpediator_local.db')
    cur_sqlite = conn_sqlite.cursor()

    cur_pg.execute("SELECT rs_id FROM snps ORDER BY rs_id")
    snps = cur_pg.fetchall()

    insert_sql = sql.SQL(
        """
        INSERT INTO snpediametadata (rs_id, gene, chromosome, position, orientation, reference, genotype, magnitude, color, summary)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (rs_id) DO UPDATE 
        SET gene = excluded.gene, 
            chromosome = excluded.chromosome, 
            position = excluded.position, 
            orientation = excluded.orientation, 
            reference = excluded.reference, 
            genotype = excluded.genotype, 
            magnitude = excluded.magnitude, 
            color = excluded.color, 
            summary = excluded.summary;
        """
    )

    last_checkpoint = read_checkpoint()
    resume = last_checkpoint is None

    for rs_id, in snps:
        if not resume:
            if rs_id == last_checkpoint:
                resume = True
            continue

        cur_sqlite.execute("SELECT rsid, gene, chromosome, position, orientation, reference, genotype, magnitude, color, summary FROM columns_db WHERE rsid = ?", (rs_id,))
        rsid_columns = cur_sqlite.fetchone()

        if rsid_columns is None:
            continue

        try:
            cur_pg.execute(insert_sql, rsid_columns)
            conn_pg.commit()
            write_checkpoint(rs_id)
        except psycopg2.IntegrityError as e:
            print(f"Integrity error on rs_id {rs_id}: {e}")
            conn_pg.rollback()
        except psycopg2.DatabaseError as e:
            print(f"Database error on rs_id {rs_id}: {e}")
            conn_pg.rollback()
        except Exception as e:
            print(f"Unknown error on rs_id {rs_id}: {e}")
            conn_pg.rollback()

except psycopg2.OperationalError as e:
    print(f"Could not connect to PostgreSQL database: {e}")
except sqlite3.OperationalError as e:
    print(f"Could not connect to SQLite database: {e}")
except Exception as e:
    print(f"An unknown error occurred: {e}")
finally:
    if cur_pg is not None:
        cur_pg.close()
    if conn_pg is not None:
        conn_pg.close()

    if cur_sqlite is not None:
        cur_sqlite.close()
