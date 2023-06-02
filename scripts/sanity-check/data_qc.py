import psycopg2
import pandas as pd

with open('../db_config.txt', 'r') as f:
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

tables = ["users", "files", "snps", "usersnps"]

for table in tables:
    cur.execute(f"SELECT * FROM {table} TABLESAMPLE SYSTEM (10)")
    
    rows = cur.fetchall()

    col_names = [desc[0] for desc in cur.description]
    
    df = pd.DataFrame(rows, columns=col_names)

    df.to_csv(f'./quality_control/{table}_sample.csv', index=False)
    
    print(f'Summary statistics for table {table}:')
    print(df.describe(include='all'))
    print("\n")

    print(f"Number of missing or NULL values in table {table}:")
    print(df.isnull().sum())
    print("\n")

    print(f"Number of duplicate records in table {table}:")
    print(df.duplicated().sum())
    print("\n")
    
    if 'user_id' in df.columns:
        print(f"Distribution of 'user_id' in table {table}:")
        print(df['user_id'].value_counts())
        print("\n")
    
    if 'rs_id' in df.columns:
        print(f"Number of unique 'rs_id' in table {table}:")
        print(df['rs_id'].nunique())
        print("\n")

    if 'created_at' in df.columns and 'updated_at' in df.columns:
        print(f"Date ranges in 'created_at' and 'updated_at' in table {table}:")
        print(f"created_at: {df['created_at'].min()} - {df['created_at'].max()}")
        print(f"updated_at: {df['updated_at'].min()} - {df['updated_at'].max()}")
        print("\n")

cur.close()
conn.close()
