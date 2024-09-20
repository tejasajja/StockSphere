"""
This script is designed to generate synthetic data for MongoDB collections related to a stock market simulation application. It creates data for three collections: agents, customers, and transactions. Users can specify the number of records to generate for each collection using command-line arguments. The script utilizes the `faker` library to generate realistic names, contacts, usernames, and other data. Pydantic models for agents and customers are used to ensure data consistency and validation before insertion into MongoDB.

The script can be executed from the command line and allows customization of the number of records to generate for each of the three collections: agents, customers, and transactions.

Usage:
    Run the script from the backend directory of your project to ensure proper import resolution. Use the following command to execute the script with default values or specify custom numbers:

    python -m app.scripts.generate_data_crypto

    This will use the default values of 10 agents, 50 customers, and 200 transactions.

Customization:
    You can customize the number of records for each collection using command-line arguments:

    --agents: Specifies the number of agents to generate. Default is 10.
    --customers: Specifies the number of customers to generate. Default is 10.
    --transactions: Specifies the number of transactions to generate. Default is 10.

    Example command with custom values:
    python -m app.scripts.generate_data_crypto --agents 20 --customers 100 --transactions 300

Requirements:
    - MongoDB running locally on the default port (27017).
    - `faker` library installed for generating synthetic data.
    - `motor` library installed for asynchronous MongoDB operations.
    - Custom Pydantic models for agents and customers located in the app.models module.

Note:
    Make sure you are in the backend directory (or the root directory where `app` is a subdirectory) when running the script to avoid import errors. Adjust import statements as necessary based on your project structure.
"""




import asyncio
import argparse
from faker import Faker
from motor.motor_asyncio import AsyncIOMotorClient
import random
import logging
from app.models import Agent, Customer, Crypto, Transaction

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

faker = Faker()

class MongoDB:
    client = None

    @classmethod
    def get_client(cls):
        if cls.client is None:
            cls.client = AsyncIOMotorClient("mongodb://localhost:27017")
        return cls.client

async def get_database():
    client = MongoDB.get_client()
    return client['stocksphere']

async def get_collections():
    db = await get_database()
    return {
        "agents": db.agents,
        "customers": db.customers,
        "transactions": db.transactions,
        "cryptocurrencies": db.cryptocurrencies
    }

async def generate_unique_id(collection, field_name):
    while True:
        unique_id = random.randint(1, 999999)
        if await collection.count_documents({field_name: unique_id}) == 0:
            return unique_id

# async def insert_customers(collections, num_customers):
#     username_counts = {}
#     for _ in range(num_customers):
#         while True:
#             name = faker.name()
#             first_name, last_name = name.split(" ")[0], name.split(" ")[-1]
#             base_username = f"{first_name[0].lower()}{last_name.lower()}"
#             if base_username in username_counts:
#                 username_counts[base_username] += 1
#                 username = f"{base_username}{username_counts[base_username]}"
#             else:
#                 username_counts[base_username] = 0
#                 username = base_username
#             if '.' not in username[-1]:
#                 break
#         email = f"{username}@crypto.com"
#         customer_data = {
#             "customer_id": await generate_unique_id(collections["customers"], "customer_id"),
#             "username": username,
#             "email": email,
#             "hashed_password": faker.md5(),
#             "balance": round(random.uniform(1000, 10000), 2),
#             "net_stock": round(random.uniform(0, 5000), 2),  
#             "role": "customer"
#         }
#         customer = Customer(**customer_data)
#         try:
#             await collections["customers"].insert_one(customer.dict(by_alias=True))
#             logging.info(f"Successfully inserted customer with ID: {customer.customer_id}, Username: {username}")
#         except Exception as e:
#             logging.error(f"Failed to insert customer: {e}")

async def generate_and_insert_transactions(collections, num_transactions):
    agents = await collections["agents"].find().to_list(length=100)
    customers = await collections["customers"].find().to_list(length=100)
    cryptos = await collections["cryptocurrencies"].find().to_list(length=100)  

    for _ in range(num_transactions):
        transaction_id = await generate_unique_id(collections["transactions"], "transaction_id")
        customer = random.choice(customers)
        agent = random.choice(agents)
        crypto = random.choice(cryptos)  

        transaction = {
            "transaction_id": transaction_id,
            "customer_id": customer["customer_id"],
            "crypto_id": crypto['crypto_id'],
            "stock_id": 0,  
            "agent_id": agent["agent_id"],
            "ticket": crypto['Symbol'],  
            "volume": random.randint(20, 100),
            "each_cost": crypto['Last_Close'],  
            "action": random.choice(['buy', 'sell']),
            "date": faker.date_time_between(start_date="-2y", end_date="now").isoformat()
        }
        try:
            await collections["transactions"].insert_one(transaction)
            logging.info(f"Successfully inserted transaction with ID: {transaction_id}, Crypto Symbol: {crypto['Symbol']}")
        except Exception as e:
            logging.error(f"Failed to insert transaction with ID {transaction_id}: {e}")

def parse_args():
    parser = argparse.ArgumentParser(description="Generate synthetic data for MongoDB.")
    parser.add_argument("--agents", type=int, default=10, help="Number of agents to generate")
    parser.add_argument("--customers", type=int, default=50, help="Number of customers to generate")
    parser.add_argument("--transactions", type=int, default=200, help="Number of transactions to generate")
    return parser.parse_args()

async def main():
    args = parse_args()
    logging.info("Script execution started.")
    collections = await get_collections()
    # await insert_agents(collections, num_agents=args.agents)
    # await insert_customers(collections, num_customers=args.customers)
    await generate_and_insert_transactions(collections, num_transactions=args.transactions)
    logging.info("Script execution completed.")

if __name__ == "__main__":
    asyncio.run(main())
