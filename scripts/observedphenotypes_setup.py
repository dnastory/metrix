import time
from bs4 import BeautifulSoup
import requests
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

def scrape_opensnp(user_id):
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

    for row in table.find_all('tr')[1:]:
        cells = row.find_all('td')
        characteristic = cells[0].text.strip()
        variation = cells[1].text.strip()

        try:
            cur.execute(
                """
                INSERT INTO observedphenotypes (user_id, characteristic, variation)
                VALUES (%s, %s, %s)
                """,
                (user_id, characteristic, variation)
            )
        except Exception as e:
            with open('error_log.txt', 'a') as f:
                f.write(f"Error inserting phenotype {characteristic} for user {user_id}: {e}\n")


cur.execute("SELECT user_id FROM Users")

for user_id, in cur.fetchall():
    scrape_opensnp(user_id)

conn.commit()

cur.close()
conn.close()
