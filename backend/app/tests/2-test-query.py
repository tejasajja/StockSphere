from pymongo import MongoClient

"""
This script connects to a MongoDB database named 'stocksphere' and runs an aggregation pipeline on the 'transactions' collection to identify the top 5 customers based on the total cost of their transactions. The calculation of total cost considers whether transactions are buys or sells, adjusting the cost accordingly.

The aggregation pipeline includes the following steps:
1. Joins 'transactions' with the 'stocks' collection, matching 'ticket' from transactions to 'Company_ticker' in stocks, and storing the result in 'stock_info'.
2. Unwinds the 'stock_info' array to simplify the structure for easier processing in subsequent steps.
3. Joins the modified transactions with the 'customers' collection, matching 'customer_id' to enrich transactions with detailed customer information, stored in 'customer_info'.
4. Unwinds the 'customer_info' to flatten the array for direct access to customer data.
5. Joins the transactions now containing stock and customer details with the 'agents' collection, matching 'agent_id' to add agent details to the transactions, stored in 'agent_info'.
6. Unwinds the 'agent_info' to simplify the document structure, allowing for easier grouping and aggregation.
7. Groups the data by 'customer_id' and calculates the 'total_cost' for each customer. This cost is computed by summing the product of 'volume', 'each_cost', and a conditional factor that is 1 for buys and -1 for sells (based on the 'action' field).
8. Sorts the results by 'total_cost' in descending order to identify customers with the highest transaction costs.
9. Limits the output to the top 5 entries to focus on the highest spenders.
10. Projects the desired fields for the final output, which includes the customer's ID, username, email, total transaction cost, agent's name, and agent's level.

The resulting list displays detailed information about the top 5 customers by transaction cost, providing insights into customer activity, transaction volumes, and the financial impact of their trading actions on the platform.

The output includes:
- Customer ID (derived from MongoDB's grouping `_id`)
- Username
- Email
- Total transaction cost (positive for buys and negative for sells)
- Agent's name
- Agent's level
"""



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
            "total_cost": {
                "$sum": {
                    "$multiply": [
                        "$volume",
                        "$each_cost",
                        {"$cond": [{"$eq": ["$action", "buy"]}, 1, -1]}
                    ]
                }
            },
            "customer_info": {"$first": "$customer_info"},
            "agent_info": {"$first": "$agent_info"}
        }
    },
    {
        "$sort": {"total_cost": -1}
    },
    {"$limit": 5},
    {
        "$project": {
            "customer_id": "$_id",
            "username": "$customer_info.username",
            "email": "$customer_info.email",
            "total_cost": 1,
            "agent_name": "$agent_info.name",
            "agent_level": "$agent_info.level"
        }
    }
]


top_customers = list(db.transactions.aggregate(pipeline))


for customer in top_customers:
    print(customer)