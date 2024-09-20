from fastapi import APIRouter, HTTPException, Request,Depends, Query
from pydantic import BaseModel, EmailStr
from fastapi.security import OAuth2PasswordRequestForm
from bson import ObjectId
from typing import List,Optional,Any
import yfinance as yf
from app.models import Customer
from app.routes.schemas import CustomerRequenst,CustomerResponse,UserAuth,TokenSchema
from fastapi import APIRouter, HTTPException
from ..database.mongo import get_collections
from bson import ObjectId
from pymongo.collection import ReturnDocument
from fastapi import APIRouter, HTTPException, status
from app.utils import authutils
from fastapi import APIRouter, HTTPException, Request,Depends
from app.routes.schemas import CustomerInfo, AgentInfo, CustomerTransactionInfo
from app.database.mongo import get_top_customers, get_top_agents, get_customers_most_transactions
from collections import defaultdict 

router = APIRouter()
    
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

class CustomerTransactionDetail(BaseModel):
    customer_id: int
    username: Optional[str]
    email: Optional[str]
    total_transactions: int
    agent_name: Optional[str]
    agent_level: Optional[str]



@router.get("/customers/most-stock-transactions", response_model=List[CustomerTransactionDetail], summary="Retrieve Top 10 Stock Customers Transactions")
async def get_customers_with_most_stock_transactions(user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"crypto_id": {"$eq": 0}}).to_list(length=None)  
    customer_ids = {t["customer_id"] for t in transactions if "customer_id" in t}
    agent_ids = {t["agent_id"] for t in transactions if "agent_id" in t}
    customers = {c["customer_id"]: c for c in await collections["customers"].find({"customer_id": {"$in": list(customer_ids)}}).to_list(length=None)}
    agents = {a["agent_id"]: a for a in await collections["agents"].find({"agent_id": {"$in": list(agent_ids)}}).to_list(length=None)}

    customer_aggregates = {}
    for transaction in transactions:
        customer_id = transaction.get("customer_id")
        if customer_id:
            if customer_id not in customer_aggregates:
                customer_aggregates[customer_id] = {
                    "total_transactions": 0,
                    "customer_info": customers.get(customer_id),
                    "agent_info": agents.get(transaction.get("agent_id"))
                }
            customer_aggregates[customer_id]["total_transactions"] += 1

    sorted_customers = sorted(customer_aggregates.items(), key=lambda x: x[1]["total_transactions"], reverse=True)[:10]    
    results = [
        CustomerTransactionDetail(
            customer_id=(key),  

            username=val["customer_info"]["username"] if val["customer_info"] else None,
            email=val["customer_info"]["email"] if val["customer_info"] else None,
            total_transactions=val["total_transactions"],
            agent_name=val["agent_info"]["name"] if val["agent_info"] else None,
            agent_level=val["agent_info"]["level"] if val["agent_info"] else None
        ) for key, val in sorted_customers
    ]
    return results

class AgentTransactionDetail(BaseModel):
    agent_id: int
    agent_name: Optional[str]
    agent_level: Optional[str]
    total_cost: float


@router.get("/agents/top-stock-transactions", response_model=List[AgentTransactionDetail], summary="Retrieve Top 10 Stock Customers")
async def get_agents_with_top_stock_transactions(user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"crypto_id": {"$eq": 0}}).to_list(length=None) 
    agent_ids = {t["agent_id"] for t in transactions if "agent_id" in t}
    agents = {a["agent_id"]: a for a in await collections["agents"].find({"agent_id": {"$in": list(agent_ids)}}).to_list(length=None)}

    agent_totals = {}
    for transaction in transactions:
        agent_id = transaction.get("agent_id")
        if agent_id:
            if agent_id not in agent_totals:
                agent_totals[agent_id] = {
                    "total_cost": 0,
                    "agent_info": agents.get(agent_id)
                }
            volume = transaction.get("volume", 0)
            each_cost = transaction.get("each_cost", 0)
            action = transaction.get("action", "")
            multiplier = 1 if action == "buy" else -1
            total_cost_contribution = volume * each_cost * multiplier

            agent_totals[agent_id]['total_cost'] += total_cost_contribution
    sorted_agents = sorted(agent_totals.items(), key=lambda x: x[1]["total_cost"], reverse=True)[:10]

    results = [
        AgentTransactionDetail(
            agent_id=(agent_id),
            agent_name=info["agent_info"]["name"] if info["agent_info"] else None,
            agent_level=info["agent_info"]["level"] if info["agent_info"] else None,
            total_cost=info["total_cost"]
        ) for agent_id, info in sorted_agents
    ]
    
    return results

class CustomerStockTransactionDetail(BaseModel):
    customer_id: int
    username: Optional[str]
    email: Optional[str]
    total_cost: float
    agent_name: Optional[str]
    agent_level: Optional[str]


@router.get("/customers/top-stock-transactions", response_model=List[CustomerStockTransactionDetail], summary="Retrieve Top 10 Stock Customers")
async def get_customers_with_top_stock_transactions(user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"crypto_id": {"$eq": 0}}).to_list(length=None)  
    stocks_dict = {stock['Company_ticker']: stock for stock in await collections["stocks"].find().to_list(length=None)}
    customers_dict = {customer['customer_id']: customer for customer in await collections["customers"].find().to_list(length=None)}
    agents_dict = {agent['agent_id']: agent for agent in await collections["agents"].find().to_list(length=None)}
    customer_aggregates = {}

    for transaction in transactions:
        stock_info = stocks_dict.get(transaction.get('ticket'))
        customer_info = customers_dict.get(transaction.get('customer_id'))
        agent_info = agents_dict.get(transaction.get('agent_id'))

        if customer_info and agent_info:
            customer_id = transaction['customer_id']
            if customer_id not in customer_aggregates:
                customer_aggregates[customer_id] = {
                    'total_cost': 0,
                    'customer_info': customer_info,
                    'agent_info': agent_info
                }

            volume = transaction.get('volume', 0)
            each_cost = transaction.get('each_cost', 0)
            action_multiplier = 1 if transaction.get('action') == 'buy' else -1
            total_cost = volume * each_cost * action_multiplier

            customer_aggregates[customer_id]['total_cost'] += total_cost
    limit = 10
    sorted_customers = sorted(customer_aggregates.items(), key=lambda x: x[1]['total_cost'], reverse=True)[:limit]

    results = [
        CustomerStockTransactionDetail(
            customer_id=(cust_id),
            username=cust['customer_info']['username'],
            email=cust['customer_info']['email'],
            total_cost=cust['total_cost'],
            agent_name=cust['agent_info']['name'] if cust['agent_info'] else None,
            agent_level=cust['agent_info']['level'] if cust['agent_info'] else None
        ) for cust_id, cust in sorted_customers
    ]
    return results


class CustomerCryptoTransactionDetail(BaseModel):
    customer_id: int
    username: Optional[str]
    email: Optional[str]
    total_cost: float
    agent_name: Optional[str]
    agent_level: Optional[str]


@router.get("/customers/top-crypto-transactions", response_model=List[CustomerCryptoTransactionDetail], summary="Retrieve Top 10 Crypto Customers Transactions")
async def get_customers_with_top_crypto_transactions(user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"stock_id": {"$eq": 0}}).to_list(length=None) 
    crypto_dict = {crypto['Symbol']: crypto for crypto in await collections["cryptocurrencies"].find().to_list(length=None)}
    customers_dict = {customer['customer_id']: customer for customer in await collections["customers"].find().to_list(length=None)}
    agents_dict = {agent['agent_id']: agent for agent in await collections["agents"].find().to_list(length=None)}
    customer_aggregates = {}
    for transaction in transactions:
        crypto_info = crypto_dict.get(transaction.get('ticket'))
        customer_info = customers_dict.get(transaction.get('customer_id'))
        agent_info = agents_dict.get(transaction.get('agent_id'))
        if customer_info and agent_info:
            customer_id = transaction['customer_id']
            if customer_id not in customer_aggregates:
                customer_aggregates[customer_id] = {
                    'total_cost': 0,
                    'customer_info': customer_info,
                    'agent_info': agent_info
                }
            volume = transaction.get('volume', 0)
            each_cost = transaction.get('each_cost', 0)
            action_multiplier = 1 if transaction.get('action') == 'buy' else -1
            total_cost = volume * each_cost * action_multiplier

            customer_aggregates[customer_id]['total_cost'] += total_cost
    limit = 10
    sorted_customers = sorted(customer_aggregates.items(), key=lambda x: x[1]['total_cost'], reverse=True)[:limit]
    results = [
        CustomerCryptoTransactionDetail(
            customer_id=(cust_id),
            username=cust['customer_info']['username'],
            email=cust['customer_info']['email'],
            total_cost=cust['total_cost'],
            agent_name=cust['agent_info']['name'] if cust['agent_info'] else None,
            agent_level=cust['agent_info']['level'] if cust['agent_info'] else None
        ) for cust_id, cust in sorted_customers
    ]
    return results

class AgentCryptoTransactionDetail(BaseModel):
    agent_id: int
    agent_name: Optional[str]
    agent_level: Optional[str]
    total_cost: float


@router.get("/agents/top-crypto-transactions", response_model=List[AgentCryptoTransactionDetail],summary="Retrieve Top 10 Crypto Agents")
async def get_agents_with_top_crypto_transactions(user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"stock_id": {"$eq": 0}}).to_list(length=None) 
    agent_ids = {t["agent_id"] for t in transactions if "agent_id" in t}
    agents = {a["agent_id"]: a for a in await collections["agents"].find({"agent_id": {"$in": list(agent_ids)}}).to_list(length=None)}
    agent_totals = {}
    for transaction in transactions:
        agent_id = transaction.get("agent_id")
        if agent_id:
            if agent_id not in agent_totals:
                agent_totals[agent_id] = {
                    "total_cost": 0,
                    "agent_info": agents.get(agent_id)
                }
            volume = transaction.get("volume", 0)
            each_cost = transaction.get("each_cost", 0)
            action = transaction.get("action", "")
            multiplier = 1 if action == "buy" else -1
            total_cost_contribution = volume * each_cost * multiplier
            agent_totals[agent_id]['total_cost'] += total_cost_contribution
    limit = 10
    sorted_agents = sorted(agent_totals.items(), key=lambda x: x[1]["total_cost"], reverse=True)[:limit]
    results = [
        AgentCryptoTransactionDetail(
            agent_id=(agent_id),
            agent_name=info["agent_info"]["name"] if info["agent_info"] else None,
            agent_level=info["agent_info"]["level"] if info["agent_info"] else None,
            total_cost=info["total_cost"]
        ) for agent_id, info in sorted_agents
    ]
    return results


class CustomerCryptoTransactionCount(BaseModel):
    customer_id: int
    username: Optional[str]
    email: Optional[str]
    total_transactions: int
    agent_name: Optional[str]
    agent_level: Optional[str]

@router.get("/customers/most-crypto-transactions", response_model=List[CustomerCryptoTransactionCount],summary="Retrieve Top 10 Crypto Customers")
async def get_customers_with_most_crypto_transactions(user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"stock_id": {"$eq": 0}}).to_list(length=None) 
    customer_ids = {t["customer_id"] for t in transactions if "customer_id" in t}
    agent_ids = {t["agent_id"] for t in transactions if "agent_id" in t}
    customers = {c["customer_id"]: c for c in await collections["customers"].find({"customer_id": {"$in": list(customer_ids)}}).to_list(length=None)}
    agents = {a["agent_id"]: a for a in await collections["agents"].find({"agent_id": {"$in": list(agent_ids)}}).to_list(length=None)}
    grouped_data = defaultdict(lambda: {'total_transactions': 0, 'customer_info': None, 'agent_info': None})
    for transaction in transactions:
        customer_id = transaction.get("customer_id")
        if customer_id:
            grouped_data[customer_id]['total_transactions'] += 1
            grouped_data[customer_id]['customer_info'] = customers.get(customer_id)
            grouped_data[customer_id]['agent_info'] = agents.get(transaction.get("agent_id"))
    limit = 10
    sorted_customers = sorted(grouped_data.items(), key=lambda x: x[1]['total_transactions'], reverse=True)[:limit]
    results = [
        CustomerCryptoTransactionCount(
            customer_id=(key),
            username=val['customer_info']['username'] if val['customer_info'] else None,
            email=val['customer_info']['email'] if val['customer_info'] else None,
            total_transactions=val['total_transactions'],
            agent_name=val['agent_info']['name'] if val['agent_info'] else None,
            agent_level=val['agent_info']['level'] if val['agent_info'] else None
        ) for key, val in sorted_customers
    ]
    return results

class CustomerStockTransactionCount(BaseModel):
    customer_id: int
    username: str | None
    email: str | None
    total_transactions: int
    agent_name: str | None
    agent_level: str | None

@router.get("/transactions/{stock_id}/most-stock-transactions", response_model=List[CustomerStockTransactionCount],summary="Retrieve Top Stock Customers Transactions by stock_id")
async def get_top_customers_for_stock(stock_id: int, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"crypto_id": {"$eq": 0}}).to_list(length=None) 
    transactions = await collections["transactions"].find({"stock_id": stock_id}).to_list(length=None)
    customer_ids = {t["customer_id"] for t in transactions if "customer_id" in t}
    agent_ids = {t["agent_id"] for t in transactions if "agent_id" in t}
    customers = {c["customer_id"]: c for c in await collections["customers"].find({"customer_id": {"$in": list(customer_ids)}}).to_list(length=None)}
    agents = {a["agent_id"]: a for a in await collections["agents"].find({"agent_id": {"$in": list(agent_ids)}}).to_list(length=None)}
    grouped_data = defaultdict(lambda: {'total_transactions': 0, 'customer_info': None, 'agent_info': None})
    for transaction in transactions:
        customer_id = transaction.get("customer_id")
        if customer_id:
            grouped_data[customer_id]['total_transactions'] += 1
            grouped_data[customer_id]['customer_info'] = customers.get(customer_id)
            grouped_data[customer_id]['agent_info'] = agents.get(transaction.get("agent_id"))
    limit = 10
    sorted_customers = sorted(grouped_data.items(), key=lambda x: x[1]['total_transactions'], reverse=True)[:limit]
    results = [
        CustomerStockTransactionCount(
            customer_id=key,
            username=val['customer_info']['username'] if val['customer_info'] else None,
            email=val['customer_info']['email'] if val['customer_info'] else None,
            total_transactions=val['total_transactions'],
            agent_name=val['agent_info']['name'] if val['agent_info'] else None,
            agent_level=val['agent_info']['level'] if val['agent_info'] else None
        ) for key, val in sorted_customers
    ]
    return results

class CustomerStockTransactionCountTicker(BaseModel):
    customer_id: int
    username: str | None
    email: str | None
    total_transactions: int
    agent_name: str | None
    agent_level: str | None

@router.get("/transactions/by-ticker/{Company_ticker}/most-stock-transactions", response_model=List[CustomerStockTransactionCountTicker],summary="Retrieve Top Stock Customers Transactions by Ticker")
async def get_top_customers_for_ticker(Company_ticker: str, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"crypto_id": {"$eq": 0}}).to_list(length=None) 
    stock_record = await collections["stocks"].find_one({"Company_ticker": Company_ticker})
    if not stock_record:
        raise HTTPException(status_code=404, detail="Stock not found")
    stock_id = stock_record['stock_id']
    transactions = await collections["transactions"].find({"stock_id": stock_id}).to_list(length=None)
    customer_ids = {t["customer_id"] for t in transactions if "customer_id" in t}
    agent_ids = {t["agent_id"] for t in transactions if "agent_id" in t}
    customers = {c["customer_id"]: c for c in await collections["customers"].find({"customer_id": {"$in": list(customer_ids)}}).to_list(length=None)}
    agents = {a["agent_id"]: a for a in await collections["agents"].find({"agent_id": {"$in": list(agent_ids)}}).to_list(length=None)}
    grouped_data = defaultdict(lambda: {'total_transactions': 0, 'customer_info': None, 'agent_info': None})
    for transaction in transactions:
        customer_id = transaction.get("customer_id")
        if customer_id:
            grouped_data[customer_id]['total_transactions'] += 1
            grouped_data[customer_id]['customer_info'] = customers.get(customer_id)
            grouped_data[customer_id]['agent_info'] = agents.get(transaction.get("agent_id"))
    limit = 10
    sorted_customers = sorted(grouped_data.items(), key=lambda x: x[1]['total_transactions'], reverse=True)[:limit]
    results = [
        CustomerStockTransactionCountTicker(
            customer_id=key,
            username=val['customer_info']['username'] if val['customer_info'] else None,
            email=val['customer_info']['email'] if val['customer_info'] else None,
            total_transactions=val['total_transactions'],
            agent_name=val['agent_info']['name'] if val['agent_info'] else None,
            agent_level=val['agent_info']['level'] if val['agent_info'] else None
        ) for key, val in sorted_customers
    ]
    return results

#####

class CustomerCryptoTransactionCount(BaseModel):
    customer_id: int
    username: str | None
    email: str | None
    total_transactions: int
    agent_name: str | None
    agent_level: str | None

@router.get("/transactions/{crypto_id}/most-stock-transactions", response_model=List[CustomerCryptoTransactionCount],summary="Retrieve Top Crypto Customers Transactions by crypto_id")
async def get_top_customers_for_crypto(crypto_id: int, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"stock_id": {"$eq": 0}}).to_list(length=None) 
    transactions = await collections["transactions"].find({"crypto_id": crypto_id}).to_list(length=None)
    customer_ids = {t["customer_id"] for t in transactions if "customer_id" in t}
    agent_ids = {t["agent_id"] for t in transactions if "agent_id" in t}
    customers = {c["customer_id"]: c for c in await collections["customers"].find({"customer_id": {"$in": list(customer_ids)}}).to_list(length=None)}
    agents = {a["agent_id"]: a for a in await collections["agents"].find({"agent_id": {"$in": list(agent_ids)}}).to_list(length=None)}
    grouped_data = defaultdict(lambda: {'total_transactions': 0, 'customer_info': None, 'agent_info': None})
    for transaction in transactions:
        customer_id = transaction.get("customer_id")
        if customer_id:
            grouped_data[customer_id]['total_transactions'] += 1
            grouped_data[customer_id]['customer_info'] = customers.get(customer_id)
            grouped_data[customer_id]['agent_info'] = agents.get(transaction.get("agent_id"))
    limit = 10
    sorted_customers = sorted(grouped_data.items(), key=lambda x: x[1]['total_transactions'], reverse=True)[:limit]
    results = [
        CustomerCryptoTransactionCount(
            customer_id=key,
            username=val['customer_info']['username'] if val['customer_info'] else None,
            email=val['customer_info']['email'] if val['customer_info'] else None,
            total_transactions=val['total_transactions'],
            agent_name=val['agent_info']['name'] if val['agent_info'] else None,
            agent_level=val['agent_info']['level'] if val['agent_info'] else None
        ) for key, val in sorted_customers
    ]
    return results

class CustomerCryptoTransactionCountTicker(BaseModel):
    customer_id: int
    username: str | None
    email: str | None
    total_transactions: int
    agent_name: str | None
    agent_level: str | None

@router.get("/transactions/by-symbol/{Symbol}/most-stock-transactions", response_model=List[CustomerCryptoTransactionCountTicker],summary="Retrieve Top Crypto Customers Transactions by Symbol")
async def get_top_customers_for_sybmol(Symbol: str, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"stock_id": {"$eq": 0}}).to_list(length=None) 
    crypto_record = await collections["cryptocurrencies"].find_one({"Symbol": Symbol})
    if not crypto_record:
        raise HTTPException(status_code=404, detail="Crypto not found")
    crypto_id = crypto_record['crypto_id']
    transactions = await collections["transactions"].find({"crypto_id": crypto_id}).to_list(length=None)
    customer_ids = {t["customer_id"] for t in transactions if "customer_id" in t}
    agent_ids = {t["agent_id"] for t in transactions if "agent_id" in t}
    customers = {c["customer_id"]: c for c in await collections["customers"].find({"customer_id": {"$in": list(customer_ids)}}).to_list(length=None)}
    agents = {a["agent_id"]: a for a in await collections["agents"].find({"agent_id": {"$in": list(agent_ids)}}).to_list(length=None)}
    grouped_data = defaultdict(lambda: {'total_transactions': 0, 'customer_info': None, 'agent_info': None})
    for transaction in transactions:
        customer_id = transaction.get("customer_id")
        if customer_id:
            grouped_data[customer_id]['total_transactions'] += 1
            grouped_data[customer_id]['customer_info'] = customers.get(customer_id)
            grouped_data[customer_id]['agent_info'] = agents.get(transaction.get("agent_id"))
    limit = 10
    sorted_customers = sorted(grouped_data.items(), key=lambda x: x[1]['total_transactions'], reverse=True)[:limit]
    results = [
        CustomerCryptoTransactionCountTicker(
            customer_id=key,
            username=val['customer_info']['username'] if val['customer_info'] else None,
            email=val['customer_info']['email'] if val['customer_info'] else None,
            total_transactions=val['total_transactions'],
            agent_name=val['agent_info']['name'] if val['agent_info'] else None,
            agent_level=val['agent_info']['level'] if val['agent_info'] else None
        ) for key, val in sorted_customers
    ]
    return results


############

class AgentStockTransactionDetail(BaseModel):
    agent_id: int
    agent_name: Optional[str]
    agent_level: Optional[str]
    total_cost: float

@router.get("/transactions/{stock_id}/top-agents", response_model=List[AgentStockTransactionDetail], summary="Retrieve Top Stock Agents by stock_id")
async def get_customers_with_most_stock_transactions(stock_id: int, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"crypto_id": {"$eq": 0}}).to_list(length=None) 
    agent_ids = {t["agent_id"] for t in transactions if "agent_id" in t}
    agents = {a["agent_id"]: a for a in await collections["agents"].find({"agent_id": {"$in": list(agent_ids)}}).to_list(length=None)}
    agent_totals = {}
    for transaction in transactions:
        agent_id = transaction.get("agent_id")
        if agent_id:
            if agent_id not in agent_totals:
                agent_totals[agent_id] = {
                    "total_cost": 0,
                    "agent_info": agents.get(agent_id)
                }
            volume = transaction.get("volume", 0)
            each_cost = transaction.get("each_cost", 0)
            action = transaction.get("action", "")
            multiplier = 1 if action == "buy" else -1
            total_cost_contribution = volume * each_cost * multiplier
            agent_totals[agent_id]['total_cost'] += total_cost_contribution
    sorted_agents = sorted(agent_totals.items(), key=lambda x: x[1]["total_cost"], reverse=True)[:10]
    results = [
        AgentStockTransactionDetail(
            agent_id=(agent_id),
            agent_name=info["agent_info"]["name"] if info["agent_info"] else None,
            agent_level=info["agent_info"]["level"] if info["agent_info"] else None,
            total_cost=info["total_cost"]
        ) for agent_id, info in sorted_agents
    ]
    
    return results


class AgentCryptoTransactionDetail(BaseModel):
    agent_id: int
    agent_name: Optional[str]
    agent_level: Optional[str]
    total_cost: float

@router.get("/transactions/{crypto_id}/top-agent", response_model=List[AgentCryptoTransactionDetail],summary="Retrieve Top Crypto Agents by crypto_id")
async def get_customers_with_most_crypto_transactions(crypto_id: int, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"stock_id": {"$eq": 0}}).to_list(length=None) 
    agent_ids = {t["agent_id"] for t in transactions if "agent_id" in t}
    agents = {a["agent_id"]: a for a in await collections["agents"].find({"agent_id": {"$in": list(agent_ids)}}).to_list(length=None)}
    agent_totals = {}
    for transaction in transactions:
        agent_id = transaction.get("agent_id")
        if agent_id:
            if agent_id not in agent_totals:
                agent_totals[agent_id] = {
                    "total_cost": 0,
                    "agent_info": agents.get(agent_id)
                }
            volume = transaction.get("volume", 0)
            each_cost = transaction.get("each_cost", 0)
            action = transaction.get("action", "")
            multiplier = 1 if action == "buy" else -1
            total_cost_contribution = volume * each_cost * multiplier
            agent_totals[agent_id]['total_cost'] += total_cost_contribution
    sorted_agents = sorted(agent_totals.items(), key=lambda x: x[1]["total_cost"], reverse=True)[:10]
    results = [
        AgentCryptoTransactionDetail(
            agent_id=(agent_id),
            agent_name=info["agent_info"]["name"] if info["agent_info"] else None,
            agent_level=info["agent_info"]["level"] if info["agent_info"] else None,
            total_cost=info["total_cost"]
        ) for agent_id, info in sorted_agents
    ]
    
    return results


class AgentStockTickerTransactionDetail(BaseModel):
    agent_id: int
    agent_name: Optional[str]
    agent_level: Optional[str]
    total_cost: float

@router.get("/transactions/by-ticker/{Company_ticker}/top-agents", response_model=List[AgentStockTickerTransactionDetail], summary="Retrieve Top Stock Agents by Ticker")
async def get_customers_with_most_stock_transactions_for_ticker(Company_ticker: str, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"crypto_id": {"$eq": 0}}).to_list(length=None) 
    agent_ids = {t["agent_id"] for t in transactions if "agent_id" in t}
    agents = {a["agent_id"]: a for a in await collections["agents"].find({"agent_id": {"$in": list(agent_ids)}}).to_list(length=None)}
    agent_totals = {}
    for transaction in transactions:
        agent_id = transaction.get("agent_id")
        if agent_id:
            if agent_id not in agent_totals:
                agent_totals[agent_id] = {
                    "total_cost": 0,
                    "agent_info": agents.get(agent_id)
                }
            volume = transaction.get("volume", 0)
            each_cost = transaction.get("each_cost", 0)
            action = transaction.get("action", "")
            multiplier = 1 if action == "buy" else -1
            total_cost_contribution = volume * each_cost * multiplier
            agent_totals[agent_id]['total_cost'] += total_cost_contribution
    sorted_agents = sorted(agent_totals.items(), key=lambda x: x[1]["total_cost"], reverse=True)[:10]
    results = [
        AgentStockTickerTransactionDetail(
            agent_id=(agent_id),
            agent_name=info["agent_info"]["name"] if info["agent_info"] else None,
            agent_level=info["agent_info"]["level"] if info["agent_info"] else None,
            total_cost=info["total_cost"]
        ) for agent_id, info in sorted_agents
    ]
    
    return results


class AgentCryptoTickerTransactionDetail(BaseModel):
    agent_id: int
    agent_name: Optional[str]
    agent_level: Optional[str]
    total_cost: float

@router.get("/transactions/by-Symbol/{Symbol}/top-agents", response_model=List[AgentCryptoTickerTransactionDetail],summary="Retrieve Top Crypto Agents by Symbol")
async def get_customers_with_most_crypto_transactions_for_ticker(Symbol: str, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"stock_id": {"$eq": 0}}).to_list(length=None) 
    agent_ids = {t["agent_id"] for t in transactions if "agent_id" in t}
    agents = {a["agent_id"]: a for a in await collections["agents"].find({"agent_id": {"$in": list(agent_ids)}}).to_list(length=None)}
    agent_totals = {}
    for transaction in transactions:
        agent_id = transaction.get("agent_id")
        if agent_id:
            if agent_id not in agent_totals:
                agent_totals[agent_id] = {
                    "total_cost": 0,
                    "agent_info": agents.get(agent_id)
                }
            volume = transaction.get("volume", 0)
            each_cost = transaction.get("each_cost", 0)
            action = transaction.get("action", "")
            multiplier = 1 if action == "buy" else -1
            total_cost_contribution = volume * each_cost * multiplier
            agent_totals[agent_id]['total_cost'] += total_cost_contribution
    sorted_agents = sorted(agent_totals.items(), key=lambda x: x[1]["total_cost"], reverse=True)[:10]
    results = [
        AgentCryptoTickerTransactionDetail(
            agent_id=(agent_id),
            agent_name=info["agent_info"]["name"] if info["agent_info"] else None,
            agent_level=info["agent_info"]["level"] if info["agent_info"] else None,
            total_cost=info["total_cost"]
        ) for agent_id, info in sorted_agents
    ]
    
    return results

####

class CustomerMostStockTransactionDetail(BaseModel):
    customer_id: int
    username: Optional[str]
    email: Optional[str]
    total_cost: float
    agent_name: Optional[str]
    agent_level: Optional[str]

@router.get("/transactions/{stock_id}/top-customers", response_model=List[CustomerMostStockTransactionDetail], summary="Retrieve Top Stock Customers by stock_id")
async def get_customers_with_top_stock_transactions(stock_id: int, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"crypto_id": {"$eq": 0}}).to_list(length=None) 
    transactions = await collections["transactions"].find({"stock_id": stock_id}).to_list(length=None)
    stocks_dict = {stock['stock_id']: stock for stock in await collections["stocks"].find().to_list(length=None)}
    customers_dict = {customer['customer_id']: customer for customer in await collections["customers"].find().to_list(length=None)}
    agents_dict = {agent['agent_id']: agent for agent in await collections["agents"].find().to_list(length=None)}

    customer_aggregates = {}
    for transaction in transactions:
        stock_info = stocks_dict.get(transaction.get('stock_id'))
        customer_info = customers_dict.get(transaction.get('customer_id'))
        agent_info = agents_dict.get(transaction.get('agent_id'))

        if customer_info and agent_info and stock_info:
            customer_id = transaction['customer_id']
            if customer_id not in customer_aggregates:
                customer_aggregates[customer_id] = {
                    'total_cost': 0,
                    'customer_info': customer_info,
                    'agent_info': agent_info
                }
            volume = transaction.get('volume', 0)
            each_cost = transaction.get('each_cost', 0)
            action_multiplier = 1 if transaction.get('action') == 'buy' else -1
            total_cost = volume * each_cost * action_multiplier
            customer_aggregates[customer_id]['total_cost'] += total_cost
    limit = 10
    sorted_customers = sorted(customer_aggregates.items(), key=lambda x: x[1]['total_cost'], reverse=True)[:limit]
    results = [
        CustomerMostStockTransactionDetail(
            customer_id=cust_id,
            username=cust['customer_info']['username'],
            email=cust['customer_info']['email'],
            total_cost=cust['total_cost'],
            agent_name=cust['agent_info']['name'] if cust['agent_info'] else None,
            agent_level=cust['agent_info']['level'] if cust['agent_info'] else None
        ) for cust_id, cust in sorted_customers
    ]

    return results

class CustomerMostCryptoTransactionDetail(BaseModel):
    customer_id: int
    username: Optional[str]
    email: Optional[str]
    total_cost: float
    agent_name: Optional[str]
    agent_level: Optional[str]

@router.get("/transactions/{crypto_id}/top-customer", response_model=List[CustomerMostCryptoTransactionDetail],summary="Retrieve Top Crypto Customers by crypto_id")
async def get_customers_with_top_stock_transactions(crypto_id: int, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"stock_id": {"$eq": 0}}).to_list(length=None) 
    transactions = await collections["transactions"].find({"crypto_id": crypto_id}).to_list(length=None)
    crypto_dict = {crypto['crypto_id']: crypto for crypto in await collections["cryptocurrencies"].find().to_list(length=None)}
    customers_dict = {customer['customer_id']: customer for customer in await collections["customers"].find().to_list(length=None)}
    agents_dict = {agent['agent_id']: agent for agent in await collections["agents"].find().to_list(length=None)}

    customer_aggregates = {}
    for transaction in transactions:
        stock_info = crypto_dict.get(transaction.get('crypto_id'))
        customer_info = customers_dict.get(transaction.get('customer_id'))
        agent_info = agents_dict.get(transaction.get('agent_id'))

        if customer_info and agent_info and stock_info:
            customer_id = transaction['customer_id']
            if customer_id not in customer_aggregates:
                customer_aggregates[customer_id] = {
                    'total_cost': 0,
                    'customer_info': customer_info,
                    'agent_info': agent_info
                }
            volume = transaction.get('volume', 0)
            each_cost = transaction.get('each_cost', 0)
            action_multiplier = 1 if transaction.get('action') == 'buy' else -1
            total_cost = volume * each_cost * action_multiplier
            customer_aggregates[customer_id]['total_cost'] += total_cost
    limit = 10
    sorted_customers = sorted(customer_aggregates.items(), key=lambda x: x[1]['total_cost'], reverse=True)[:limit]
    results = [
        CustomerMostCryptoTransactionDetail(
            customer_id=cust_id,
            username=cust['customer_info']['username'],
            email=cust['customer_info']['email'],
            total_cost=cust['total_cost'],
            agent_name=cust['agent_info']['name'] if cust['agent_info'] else None,
            agent_level=cust['agent_info']['level'] if cust['agent_info'] else None
        ) for cust_id, cust in sorted_customers
    ]

    return results

class CustomerMostStockTickerTransactionDetail(BaseModel):
    customer_id: int
    username: Optional[str]
    email: Optional[str]
    total_cost: float
    agent_name: Optional[str]
    agent_level: Optional[str]
    
@router.get("/transactions/by-ticker/{Company_ticker}/top-customers", response_model=List[CustomerMostStockTickerTransactionDetail],summary="Retrieve Top Stock Customers by Ticker" )
async def get_customers_with_top_stock_transactions_by_ticker(Company_ticker: str, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"crypto_id": {"$eq": 0}}).to_list(length=None) 
    stock_record = await collections["stocks"].find_one({"Company_ticker": Company_ticker})
    if not stock_record:
        raise HTTPException(status_code=404, detail="Ticker not found")
    stock_id = stock_record['stock_id']
    transactions = await collections["transactions"].find({"stock_id": stock_id}).to_list(length=None)
    customers_dict = {customer['customer_id']: customer for customer in await collections["customers"].find().to_list(length=None)}
    agents_dict = {agent['agent_id']: agent for agent in await collections["agents"].find().to_list(length=None)}
    customer_aggregates = {}
    for transaction in transactions:
        customer_info = customers_dict.get(transaction.get('customer_id'))
        agent_info = agents_dict.get(transaction.get('agent_id'))

        if customer_info and agent_info:
            customer_id = transaction['customer_id']
            if customer_id not in customer_aggregates:
                customer_aggregates[customer_id] = {
                    'total_cost': 0,
                    'customer_info': customer_info,
                    'agent_info': agent_info
                }
            volume = transaction.get('volume', 0)
            each_cost = transaction.get('each_cost', 0)
            action_multiplier = 1 if transaction.get('action') == 'buy' else -1
            total_cost = volume * each_cost * action_multiplier
            customer_aggregates[customer_id]['total_cost'] += total_cost
    limit = 10
    sorted_customers = sorted(customer_aggregates.items(), key=lambda x: x[1]['total_cost'], reverse=True)[:limit]
    results = [
        CustomerMostStockTickerTransactionDetail(
            customer_id=cust_id,
            username=cust['customer_info']['username'],
            email=cust['customer_info']['email'],
            total_cost=cust['total_cost'],
            agent_name=cust['agent_info']['name'] if cust['agent_info'] else None,
            agent_level=cust['agent_info']['level'] if cust['agent_info'] else None
        ) for cust_id, cust in sorted_customers
    ]
    return results


class CustomerMostCryptoSymbolTransactionDetail(BaseModel):
    customer_id: int
    username: Optional[str]
    email: Optional[str]
    total_cost: float
    agent_name: Optional[str]
    agent_level: Optional[str]
    
@router.get("/transactions/by-Symbol/{Symbol}/top-customers", response_model=List[CustomerMostCryptoSymbolTransactionDetail], summary="Retrieve Top Crypto Customers by Symbol")
async def get_customers_with_top_stock_transactions_by_ticker(Symbol: str, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"stock_id": {"$eq": 0}}).to_list(length=None) 
    crypto_record = await collections["cryptocurrencies"].find_one({"Symbol": Symbol})
    if not crypto_record:
        raise HTTPException(status_code=404, detail="Symbol not found")
    crypto_id = crypto_record['crypto_id']
    transactions = await collections["transactions"].find({"crypto_id": crypto_id}).to_list(length=None)
    customers_dict = {customer['customer_id']: customer for customer in await collections["customers"].find().to_list(length=None)}
    agents_dict = {agent['agent_id']: agent for agent in await collections["agents"].find().to_list(length=None)}
    customer_aggregates = {}
    for transaction in transactions:
        customer_info = customers_dict.get(transaction.get('customer_id'))
        agent_info = agents_dict.get(transaction.get('agent_id'))

        if customer_info and agent_info:
            customer_id = transaction['customer_id']
            if customer_id not in customer_aggregates:
                customer_aggregates[customer_id] = {
                    'total_cost': 0,
                    'customer_info': customer_info,
                    'agent_info': agent_info
                }
            volume = transaction.get('volume', 0)
            each_cost = transaction.get('each_cost', 0)
            action_multiplier = 1 if transaction.get('action') == 'buy' else -1
            total_cost = volume * each_cost * action_multiplier
            customer_aggregates[customer_id]['total_cost'] += total_cost
    limit = 10
    sorted_customers = sorted(customer_aggregates.items(), key=lambda x: x[1]['total_cost'], reverse=True)[:limit]
    results = [
        CustomerMostCryptoSymbolTransactionDetail(
            customer_id=cust_id,
            username=cust['customer_info']['username'],
            email=cust['customer_info']['email'],
            total_cost=cust['total_cost'],
            agent_name=cust['agent_info']['name'] if cust['agent_info'] else None,
            agent_level=cust['agent_info']['level'] if cust['agent_info'] else None
        ) for cust_id, cust in sorted_customers
    ]
    return results


