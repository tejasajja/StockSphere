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
            "from": "agents",  
            "localField": "agent_id",
            "foreignField": "agent_id",  
            "as": "agent_info"
        }
    },
    {"$unwind": "$agent_info"},
    {
        "$group": {
            "_id": "$agent_id",
            "total_cost": {
                "$sum": {
                    "$multiply": [
                        "$volume",
                        "$each_cost",
                        {"$cond": [{"$eq": ["$action", "buy"]}, 1, -1]}
                    ]
                }
            },
            "agent_info": {"$first": "$agent_info"}
        }
    },
    {
        "$sort": {"total_cost": -1}
    },
    {"$limit": 5},
    {
        "$project": {
            "agent_id": "$_id",
            "agent_name": "$agent_info.name",
            "agent_level": "$agent_info.level",
            "total_cost": 1
        }
    }
]

# Execute the query
top_agents = list(db.transactions.aggregate(pipeline))

# Printing the results
for agent in top_agents:
    print(agent)
