import mwclient
from mwclient import Site
import os
import sqlite3
from bs4 import BeautifulSoup

agent = 'Metrix bot Using mwclient/' + mwclient.__ver__

site = mwclient.Site(('https', 'bots.snpedia.com'), path='/', clients_useragent=agent)

os.makedirs('../data/SNPedia', exist_ok=True)

conn_sqlite = sqlite3.connect('/home/ec2-user/.local/share/snpediator/snpediator_local.db')
cur_sqlite = conn_sqlite.cursor()

cur_sqlite.execute("SELECT rs_id FROM snp")
snps = [rs_id[0] for rs_id in cur_sqlite.fetchall()]

for i, rs_id in enumerate(snps):
    try:
        page = site.pages[rs_id]
        if not page.exists:
            print(f"SNP {rs_id} does not exist on SNPedia.")
            continue

        print(f"Fetching SNP {i+1}: {rs_id}")

        snp_page = page.getWikiText()

        snp_html = site.expandtemplates(snp_page)

        soup = BeautifulSoup(snp_html, 'html.parser')
        content = soup.find(class_='mw-body content')

        with open(f'../data/SNPedia/{rs_id}.html', 'w') as f:
            f.write(str(content))

    except Exception as e:
        print(f"Failed to fetch SNP {rs_id}. Error: {e}")

print("Done fetching SNP data.")

cur_sqlite.close()
conn_sqlite.close()
