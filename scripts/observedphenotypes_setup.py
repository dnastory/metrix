import logging
import time
from bs4 import BeautifulSoup
import requests
import psycopg2
from psycopg2 import sql

logging.basicConfig(filename='observedphenotypes_setup.log', level=logging.INFO)

def get_db_config():
    with open('./db_config.txt', 'r') as f:
        db_config = [line.strip() for line in f.readlines()]
        return db_config

def scrape_opensnp(user_id, cur, conn):
    """
    Scrape the user's OpenSNP page and insert the phenotypes into the database.

    :param user_id: The user ID.
    """
    url = f"https://opensnp.org/users/{user_id}"
    
    logging.info(f"Scraping phenotypes for user_id: {user_id}")
    
    time.sleep(1)

    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        logging.error(f"Request error for user {user_id}: {e}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    if "This user has not entered any phenotypes yet." in soup.text:
        logging.info(f"No phenotypes found for user_id: {user_id}")
        return
    
    table = soup.find('table', {'class': 'table table-hover'})

    if table is None:
        logging.warning(f"No phenotype table found for user_id: {user_id}")
        return

    insert_sql = sql.SQL(
        """
        INSERT INTO observedphenotypes (user_id, characteristic, variation)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id, characteristic) DO UPDATE 
        SET variation = excluded.variation;
        """
    )

    for row in table.find_all('tr')[1:]:
        cells = row.find_all('td')
        characteristic = cells[0].text.strip()
        variation = cells[1].text.strip()

        try:
            cur.execute(insert_sql, (user_id, characteristic, variation))
            conn.commit()
            logging.info(f"Inserted phenotype {characteristic} with variation {variation} for user {user_id}")
        except psycopg2.DatabaseError as e:
            logging.error(f"Database error on phenotype {characteristic} for user {user_id}: {e}")
            conn.rollback()
        except Exception as e:
            logging.error(f"Unknown error on phenotype {characteristic} for user {user_id}: {e}")
            conn.rollback()


if __name__ == "__main__":
    db_name, db_user, db_password, db_host, db_port = get_db_config()

    conn = psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM Users")
    user_ids = cur.fetchall()
    for i, (user_id,) in enumerate(user_ids):
        scrape_opensnp(user_id, cur, conn)

        if i % 10 == 0:  # Every 10 users, log the count
            cur.execute("SELECT COUNT(*) FROM observedphenotypes")
            count = cur.fetchone()[0]
            logging.info(f"Processed {i} users, observedphenotypes table now has {count} rows.")
    
    conn.close()

    logging.info("Finished processing phenotypes 🙌")
