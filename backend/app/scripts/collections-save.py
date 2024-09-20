from pymongo import MongoClient
import json
import os


client = MongoClient('mongodb://localhost:27017/')
db = client['stocksphere']

json_dir = '../collections'
os.makedirs(json_dir, exist_ok=True)  


for collection_name in db.list_collection_names():
    collection = db[collection_name]
    documents = collection.find({})
    documents_list = list(documents)  
    file_path = os.path.join(json_dir, f'{collection_name}.json')
    with open(file_path, 'w') as file:
        json.dump(documents_list, file, default=str)  
