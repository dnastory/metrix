import sqlite3
import psycopg2
from psycopg2 import sql

with open('./db_config.txt', 'r') as f:
    db_config = [line.strip() for line in f.readlines()]
    db_name, db_user, db_password, db_host, db_port = db_config


conn_pg = None
conn_sqlite = None

try:
    conn_pg = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    cur_pg = conn_pg.cursor()

    # TMP: modify the snpediametadata table to include chromosome and genotype fields	
    cur_pg.execute("ALTER TABLE snpediametadata ADD COLUMN IF NOT EXISTS chromosome TEXT, ADD COLUMN IF NOT EXISTS genotype TEXT;")	
    conn_pg.commit()


    conn_sqlite = sqlite3.connect('/home/ec2-user/.local/share/snpediator/snpediator_local.db')
    cur_sqlite = conn_sqlite.cursor()

    cur_pg.execute("SELECT rs_id FROM snp")
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

    for rs_id, in snps:
        cur_sqlite.execute("SELECT rsid, gene, chromosome, position, orientation, reference, genotype, magnitude, color, summary FROM columns_db WHERE rsid = ?", (rs_id,))
        rsid_columns = cur_sqlite.fetchone()

        if rsid_columns is None:
            continue

        cur_pg.execute(insert_sql, rsid_columns)

    conn_pg.commit()

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    if cur_pg is not None:
        cur_pg.close()
    if conn_pg is not None:
        conn_pg.close()

    if cur_sqlite is not None:
        cur_sqlite.close()