import mwclient
import os
import psycopg2
from requests import exceptions
from bs4 import BeautifulSoup
import json
import tenacity
from dotenv import load_dotenv
import requests
import logging

logging.basicConfig(filename='batch_snpedia_html.log', level=logging.INFO)

load_dotenv()

def get_db_config():
    db_config = [os.getenv("DB_NAME"), os.getenv("DB_USER"), os.getenv("DB_PASSWORD")]
    return db_config

@tenacity.retry(stop=tenacity.stop_after_attempt(3), wait=tenacity.wait_fixed(1),
                retry=(exceptions.Timeout, exceptions.ConnectionError))
def call_gpt4_api(text):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": os.getenv("OPENAI_API_KEY")
    }
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": "You are a helpful genomic data review specialist. Your job is to provide simple, clear, and helpful insights about bio-information."},
            {"role": "user", "content": f"Extract key information about this SNP: {text}"}
        ],
        "temperature": 0.05,
        "max_tokens": 600,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()['choices'][0]['message']['content']

agent = 'Metrix bot Using mwclient/' + mwclient.__version__
site = mwclient.Site(('https', 'bots.snpedia.com'), path='/', clients_useragent=agent)

db_config = get_db_config()

with psycopg2.connect(database=db_config[0], user=db_config[1], password=db_config[2]) as conn_psql:
    with conn_psql.cursor() as cur_psql:

        cur_psql.execute("SELECT rs_id FROM snpediametadata")
        snps = [rs_id[0] for rs_id in cur_psql.fetchall()]

        existing_links = set()

        if os.path.exists('../data/SNPedia/txt/list.txt'):
            with open('../data/SNPedia/txt/list.txt', 'r') as f:
                existing_links = set(f.read().splitlines())

        for i, rs_id in enumerate(snps):
            try:
                page = site.pages[rs_id]
                if not page.exists:
                    logging.info(f"SNP {rs_id} does not exist on SNPedia.")
                    continue

                logging.info(f"Processing SNP {i+1}: {rs_id}")

                snp_page = page.text()
                snp_html = site.expandtemplates(snp_page, title=rs_id, generatexml=True)

                soup = BeautifulSoup(snp_html, 'html.parser')
                content = soup.find(class_='mw-body content')

                with open(f'../data/SNPedia/html/{rs_id}.html', 'w') as f:
                    f.write(str(content))

                p_li_content = [tag.get_text() for tag in soup.select('.mw-parser-output p, .mw-parser-output li')]
                with open(f'../data/SNPedia/txt/{rs_id}.txt', 'w') as f:
                    f.writelines(p_li_content)

                linked_rs_ids = [a['href'].split('/')[-1] for a in soup.select('.mw-parser-output a') if a['href'].startswith("https://bots.snpedia.com/index.php/")]

                for linked_rs_id in linked_rs_ids:
                    if linked_rs_id not in existing_links:
                        logging.info(f"Processing linked SNP: {linked_rs_id}")
                        page = site.pages[linked_rs_id]
                        if not page.exists:
                            continue

                        snp_page = page.getWikiText()

                        snp_html = site.expandtemplates(snp_page)

                        soup = BeautifulSoup(snp_html, 'html.parser')

                        p_li_content = [tag.get_text() for tag in soup.select('.mw-parser-output p, .mw-parser-output li')]
                        with open(f'../data/SNPedia/txt/{linked_rs_id}.txt', 'w') as f:
                            f.writelines(p_li_content)

                        existing_links.add(linked_rs_id)

                with open('../data/SNPedia/txt/list.txt', 'w') as f:
                    f.writelines(existing_links)

                txt_files = [f'../data/SNPedia/txt/{rs_id}.txt'] + [f'../data/SNPedia/txt/{linked_rs_id}.txt' for linked_rs_id in linked_rs_ids if linked_rs_id in existing_links]

                llm_summary = ''
                for txt_file in txt_files:
                    with open(txt_file, 'r') as f:
                        txt_content = f.read()

                    llm_summary = call_gpt4_api(txt_content)
                    logging.info(f"LLM Summary for SNP {rs_id}: {llm_summary}")

                cur_psql.execute("INSERT INTO snpedia_unstructured (rs_id, html, txt, llm_summary) VALUES (%s, %s, %s, %s)", (rs_id, f'../data/SNPedia/html/{rs_id}.html', txt_files, llm_summary))

            except Exception as e:
                print(f"Failed to fetch SNP {rs_id}. Error: {e}")
                logging.error(f"Failed to fetch SNP {rs_id}. Error: {e}")

    conn_psql.commit()

print("Done fetching SNP data 🐁")

cur_psql.close()
conn_psql.close()
