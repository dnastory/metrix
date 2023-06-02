import time
from bs4 import BeautifulSoup
import requests
from psycopg2 import sql

def get_db_config():
    with open('./db_config.txt', 'r') as f:
        db_config = [line.strip() for line in f.readlines()]
        return db_config

def scrape_opensnp(user_id, cur):
    """
    Scrape the user's OpenSNP page and insert the phenotypes into the database.

    :param user_id: The user ID.
    """
    url = f"https://opensnp.org/users/{user_id}"
    
    time.sleep(1)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    if "This user has not entered any phenotypes yet." in soup.text:
        return
    
    table = soup.find('table', {'class': 'table table-hover'})

    if table is None:
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

        try {
            cur.execute(insert_sql, (user_id, characteristic, variation))
        except psycopg2.DatabaseError as e:
            print(f"Database error on phenotype {characteristic} for user {user_id}: {e}")
            conn.rollback()
        except Exception as e:
            print(f"Unknown error on phenotype {characteristic} for user {user_id}: {e}")
            conn.rollback()

if __name__ == "__main__":
    db_name, db_user, db_password, db_host, db_port = get_db_config()

    with psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM Users")
            for user_id, in cur.fetchall():
                scrape_opensnp(user_id, cur)

            conn.commit()

    print("Finished processing phenotypes 🙌")
