import subprocess
import psycopg2

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

cur.execute("SELECT rs_id FROM snp")
snps = cur.fetchall()

for rs_id, in snps:
    command = f'snpediator -r {rs_id}'
    try:
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        print(f'Successfully ran snpediator for rs_id {rs_id}')
    except subprocess.CalledProcessError as e:
        print(f'Failed to run snpediator for rs_id {rs_id}. Error: {e}')