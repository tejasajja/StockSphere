from pymongo import MongoClient
import pymongo.errors  # Import pymongo errors module
import json
import os

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['stocksphere']

# Define the directory where JSON files are stored
json_dir = '../collections'

# Mapping of collections to their unique identifiers
unique_keys = {
    'agents': ['_id', 'agent_id'],
    'crypto_history': '_id',
    'cryptocurrencies': '_id',
    'customers': '_id',
    'stock_history': '_id',
    'stocks': ['_id', 'Company_ticker', 'stock_id'],
    'transactions': '_id'
}

# Load each JSON file and ensure the database is up to date
for json_file in os.listdir(json_dir):
    if json_file.endswith('.json'):
        collection_name = json_file[:-5]  # Remove '.json' from the filename to get the collection name
        collection = db[collection_name]

        file_path = os.path.join(json_dir, json_file)
        with open(file_path, 'r') as file:
            data = json.load(file)
            unique_key = unique_keys.get(collection_name, '_id')  # Default to '_id' if not specified

            for document in data:
                if isinstance(unique_key, list):  # Handle multiple keys for complex unique identifiers
                    query = {key: document.get(key) for key in unique_key if key in document}
                else:
                    query = {unique_key: document.get(unique_key)} if unique_key in document else None

                if query:
                    existing_doc = collection.find_one(query)
                    if existing_doc:
                        collection.update_one(query, {'$set': document})
                    else:
                        try:
                            collection.insert_one(document)
                        except pymongo.errors.DuplicateKeyError as e:
                            print(f"Duplicate key error when trying to insert: {e.details}")
                else:
                    print(f"Document missing unique identifier '{unique_key}', not inserted: {document}")
