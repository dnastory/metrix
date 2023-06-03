import os
import psycopg2
import requests
import logging
from requests import exceptions
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from psycopg2 import errors

load_dotenv()

logging.basicConfig(filename='batch_snpedia_html.log', level=logging.INFO)

def get_db_config():
    db_config = [os.getenv("DB_NAME"), os.getenv("DB_USER"), os.getenv("DB_PASSWORD")]
    return db_config

def call_gpt4_api(text, snp_id):
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": os.getenv("OPENAI_API_KEY")
        }
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "You are a helpful genomic data review specialist. Your job is to provide simple, clear, and helpful insights about bio-information."},
                {"role": "user", "content": f"My notes on SNP {snp_id}: {text} \
                 Summarize evidence-based knowledge about {snp_id}. No need to caveat your summary, and do not make up unsubstantiated claims. If this SNP is correlated with a health outcome, make sure to mention symptoms that would support a positive or negative diagnosis. End your message with 10 specific tags (in CamelCase) about what kind of category, influence, or origin this SNP has: e.g. #Personality, #Health, #Appearance, and so on. Unacceptable tags are #SNP, #Genetic, #GeneticDisorder, #{snp_id}. If there is insufficient research, a single tag #Unknown will do."}
            ],
            "temperature": 0.05,
            "max_tokens": 600,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        response = requests.post(url, headers=headers, json=data)
        content = response.json()['choices'][0]['message']['content']
        return content
    except (exceptions.Timeout, exceptions.ConnectionError) as e:
        logging.error(f"Failed to fetch LLM Summary for SNP {snp_id}. Error: {e}")
        return None

db_config = get_db_config()

with psycopg2.connect(database=db_config[0], user=db_config[1], password=db_config[2]) as conn_psql:
    with conn_psql.cursor() as cur_psql:

        cur_psql.execute("SELECT rs_id FROM snpediametadata")
        snps = [rs_id[0] for rs_id in cur_psql.fetchall()]

        for i, rs_id in enumerate(snps):
            try:

                cur_psql.execute("SELECT COUNT(*) FROM snpedia_unstructured WHERE rs_id = %s", (rs_id,))

                if cur_psql.fetchone()[0] != 0:
                    logging.info(f"SNP {rs_id} already exists in the database. Skipping.")
                    continue

                url = f"https://bots.snpedia.com/index.php/{rs_id}"
                page = requests.get(url)

                if page.status_code != 200:
                    logging.info(f"SNP {rs_id} does not exist on SNPedia.")
                    continue

                logging.info(f"Processing SNP {i+1}: {rs_id}")

                soup = BeautifulSoup(page.content, 'html.parser')

                content = soup.find(class_='mw-body content')

                with open(f'../data/SNPedia/html/{rs_id}.html', 'w') as f:
                    f.write(str(content))

                p_li_content = [tag.get_text().replace("Have questions? Visit https://www.reddit.com/r/SNPedia", "") for tag in soup.select('.mw-parser-output p, .mw-parser-output li, tbody')]

                txt_file_path = f'../data/SNPedia/txt/{rs_id}.txt'
                with open(txt_file_path, 'w') as f:
                    f.writelines(p_li_content)

                with open(txt_file_path, 'r') as f:
                    txt_content = f.read()

                llm_summary = call_gpt4_api(txt_content, rs_id)

                if llm_summary is None:
                    logging.error(f"Could not get LLM Summary for SNP {rs_id}. Adding SNP data without LLM Summary.")
                
                logging.info(f"LLM Summary for SNP {rs_id}: {llm_summary}")

                cur_psql.execute("INSERT INTO snpedia_unstructured (rs_id, html, txt, llm_summary) VALUES (%s, %s, %s, %s)", (rs_id, f'../data/SNPedia/html/{rs_id}.html', txt_file_path, llm_summary))

                conn_psql.commit()

            except errors.UniqueViolation as e:
                logging.error(f"Duplicate SNP {rs_id}. Error: {e}")
                conn_psql.rollback()

            except Exception as e:
                print(f"Failed to fetch SNP {rs_id}. Error: {e}")
                logging.error(f"Failed to fetch SNP {rs_id}. Error: {e}")
                conn_psql.rollback()
                

        print("Done fetching SNP data 🐁")

        cur_psql.close()
        conn_psql.close()




