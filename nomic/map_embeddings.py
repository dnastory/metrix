import os
import glob
import nomic
from nomic import atlas
from dotenv import load_dotenv
import pickle

load_dotenv()
api_key = os.getenv("NOMIC_API_KEY")

nomic.login(api_key)

if os.path.exists('documents.pkl'):
    with open('documents.pkl', 'rb') as file:
        documents = pickle.load(file)
else:
    documents = []
    file_paths = glob.glob('../opensnp_txt/*.txt')
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            text = file.read()
            document = {'id': file_path, 'text': text}
            documents.append(document)
    with open('documents.pkl', 'wb') as file:
        pickle.dump(documents, file)

project = atlas.map_text(
    data=documents,
    id_field='id',
    indexed_field='text',
    description='openSNPs'
)

project.maps[0]
