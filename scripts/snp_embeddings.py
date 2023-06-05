import chromadb
import pandas as pd

chroma_client = chromadb.Client()
collection = chroma_client.create_collection(name="snp_collection")

merged_data = pd.read_csv("/home/ec2-user/hackathon/metrix/data/merged_data.csv")
snpedia_unstructed = pd.read_csv("/home/ec2-user/hackathon/metrix/data/snpedia_unstructured.csv")

merged_data = pd.merge(merged_data, snpedia_unstructed, on='rs_id', how='left')
merged_data = merged_data[['rs_id', 'user_id', 'llm_summary']]
merged_data['user_id'] = merged_data['user_id'].astype(int)
merged_data['llm_summary'] = merged_data['llm_summary'].fillna('')

for index, row in merged_data.iterrows():
    unique_id = f"{row['user_id']}_{row['rs_id']}"
    collection.add(
        documents=[row['llm_summary']],
        metadatas=[row.to_dict()],
        ids=[unique_id]
    )

user_data = merged_data[['rs_id', 'user_id']].copy()
user_data['unique_id'] = user_data['user_id'].astype(str) + '_' + user_data['rs_id']

def get_user_snps(query, user_id, num_results=150):
    results = collection.query(
        query_texts=[query],
        n_results=num_results
    )
    
    unique_ids = results['ids'][0]
    rs_ids = [id.split('_')[1] for id in unique_ids if id.split('_')[0] == str(user_id)]
    print(len(rs_ids), rs_ids)

    user_snps = user_data[(user_data['user_id'] == user_id) & (user_data['rs_id'].isin(rs_ids))]
    
    return user_snps

print(get_user_snps("heart", 6043)) 
print(get_user_snps("immunity", 6381))
print(get_user_snps("lungs", 6381))
print(get_user_snps("autism", 6381))
print(get_user_snps("healthy", 6381))
