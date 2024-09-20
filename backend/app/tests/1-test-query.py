from pymongo import MongoClient


client = MongoClient('mongodb://localhost:27017/')
db = client['stocksphere']  


pipeline = [
    {
        "$lookup": {
            "from": "stocks",  
            "localField": "ticket",
            "foreignField": "Company_ticker",  
            "as": "stock_info"
        }
    },
    {"$unwind": "$stock_info"},  
    {
        "$lookup": {
            "from": "customers", 
            "localField": "customer_id",
            "foreignField": "customer_id",  
            "as": "customer_info"
        }
    },
    {"$unwind": "$customer_info"},
    {
        "$lookup": {
            "from": "agents",  
            "localField": "agent_id",
            "foreignField": "agent_id", 
            "as": "agent_info"
        }
    },
    {"$unwind": "$agent_info"},
    {
        "$group": {
            "_id": "$customer_id",
            "total_transactions": {"$sum": 1},
            "customer_info": {"$first": "$customer_info"},
            "agent_info": {"$first": "$agent_info"}
        }
    },
    {
        "$sort": {"total_transactions": -1}
    },
    {"$limit": 5},
    {
        "$project": {
            "customer_id": "$_id",
            "username": "$customer_info.username",
            "email": "$customer_info.email",
            "total_transactions": 1,
            "agent_name": "$agent_info.name",
            "agent_level": "$agent_info.level"
        }
    }
]

# Execute the query
customers_most_transactions = list(db.transactions.aggregate(pipeline))

# Printing the results
for customer in customers_most_transactions:
    print(customer)