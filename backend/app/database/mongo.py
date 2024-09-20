from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Depends
import pymongo
from pymongo import mongo_client
import asyncio

class MongoDB:
    client = None

    @classmethod
    def get_client(cls):
        if cls.client is None:
            cls.client = AsyncIOMotorClient("mongodb://localhost:27017")
        return cls.client

async def get_database():
    client = MongoDB.get_client()
    return client.stocksphere

async def get_collections():
    db = await get_database()
    collections = {
        "agents": db.agents,
        "customers": db.customers,
        "stocks": db.stocks,
        "stock_history": db.stock_history,
        "transactions": db.transactions,
        "cryptocurrencies" : db.cryptocurrencies,
        "crypto_history" : db.crypto_history
    }
    await collections["stocks"].create_index([("stock_id", pymongo.ASCENDING)], unique=True)
    await collections["stocks"].create_index([("Company_ticker", pymongo.ASCENDING)], unique=True)
    
    await collections["agents"].create_index([("agent_id", pymongo.ASCENDING)], unique=True)
    return collections

async def get_user():
    db = await get_database()
    User = db.users
    User.create_index([("email", pymongo.ASCENDING)], unique=True)
    return User




from fastapi import FastAPI, WebSocket
from pymongo import MongoClient
from starlette.websockets import WebSocketDisconnect

app = FastAPI()

client = MongoClient("mongodb://localhost:27017")
db = client["stocksphere"]

connected_clients = []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        
        with db.watch() as stream:
            for change in stream:
                for client in connected_clients:
                    await client.send_json(change)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print("Client disconnected")

async def get_top_customers(limit: int):
    pipeline = [
        {"$lookup": {"from": "stocks", "localField": "ticket", "foreignField": "Company_ticker", "as": "stock_info"}},
        {"$unwind": "$stock_info"},
        {"$lookup": {"from": "customers", "localField": "customer_id", "foreignField": "customer_id", "as": "customer_info"}},
        {"$unwind": "$customer_info"},
        {"$lookup": {"from": "agents", "localField": "agent_id", "foreignField": "agent_id", "as": "agent_info"}},
        {"$unwind": "$agent_info"},
        {"$group": {
            "_id": "$customer_id",
            "total_cost": {
                "$sum": {
                    "$multiply": ["$volume", "$each_cost", {"$cond": [{"$eq": ["$action", "buy"]}, 1, -1]}]
                }
            },
            "customer_info": {"$first": "$customer_info"},
            "agent_info": {"$first": "$agent_info"}
        }},
        {"$sort": {"total_cost": -1}},
        {"$limit": limit},
        {"$project": {
            "customer_id": "$_id",
            "username": "$customer_info.username",
            "email": "$customer_info.email",
            "total_cost": 1,
            "agent_name": "$agent_info.name",
            "agent_level": "$agent_info.level"
        }}
    ]

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: list(db.transactions.aggregate(pipeline)))


async def get_top_agents(limit: int):
    pipeline = [
        {"$lookup": {
            "from": "stocks",
            "localField": "ticket",
            "foreignField": "Company_ticker",
            "as": "stock_info"
        }},
        {"$unwind": "$stock_info"},
        {"$lookup": {
            "from": "agents",
            "localField": "agent_id",
            "foreignField": "agent_id",
            "as": "agent_info"
        }},
        {"$unwind": "$agent_info"},
        {"$group": {
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
        }},
        {"$sort": {"total_cost": -1}},
        {"$limit": limit},
        {"$project": {
            "agent_id": "$_id",
            "agent_name": "$agent_info.name",
            "agent_level": "$agent_info.level",
            "total_cost": 1
        }}
    ]

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: list(db.transactions.aggregate(pipeline)))

async def get_customers_most_transactions(limit: int):
    pipeline = [
        {"$lookup": {
            "from": "stocks",
            "localField": "ticket",
            "foreignField": "Company_ticker",
            "as": "stock_info"
        }},
        {"$unwind": "$stock_info"},
        {"$lookup": {
            "from": "customers",
            "localField": "customer_id",
            "foreignField": "customer_id",
            "as": "customer_info"
        }},
        {"$unwind": "$customer_info"},
        {"$lookup": {
            "from": "agents",
            "localField": "agent_id",
            "foreignField": "agent_id",
            "as": "agent_info"
        }},
        {"$unwind": "$agent_info"},
        {"$group": {
            "_id": "$customer_id",
            "total_transactions": {"$sum": 1},
            "customer_info": {"$first": "$customer_info"},
            "agent_info": {"$first": "$agent_info"}
        }},
        {"$sort": {"total_transactions": -1}},
        {"$limit": limit},
        {"$project": {
            "customer_id": "$_id",
            "username": "$customer_info.username",
            "email": "$customer_info.email",
            "total_transactions": 1,
            "agent_name": "$agent_info.name",
            "agent_level": "$agent_info.level"
        }}
    ]

    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: list(db.transactions.aggregate(pipeline)))
