from fastapi import APIRouter, HTTPException, Request

from typing import List, Optional
# import yfinance as yf
from fastapi import APIRouter, Depends, Query
from datetime import datetime
from app.models import Transaction,Customer,Stock
from app.routes.schemas import TransactionRequest ,TransactionAdminRequest,Cstock,Transactionpro
from fastapi import APIRouter, HTTPException
from app.database.mongo import get_collections
from app.utils import authutils
from fastapi import APIRouter, HTTPException, Request,Depends
from pymongo.collection import ReturnDocument
from fastapi import APIRouter, HTTPException, status


router = APIRouter()

@router.get("/", response_model=list[Transaction])
async def get_stocks( user: Customer = Depends(authutils.get_current_user)):
    userid=user.customer_id
    collections = await get_collections()
    transaction_data = await collections["transactions"].find({"customer_id": userid}).to_list(length=100)
    
    return transaction_data

@router.get("/customer/stocks", response_model=List[Transaction])
async def get_customer_stock_transactions(user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    userid=user.customer_id
    # Assuming 'stock_id' is used to identify stock transactions {"crypto_id": {"$eq": 0}}
    transactions = await collections["transactions"].find({"customer_id": userid, "crypto_id": {"$eq": 0}}).to_list(length=100)
    return transactions

@router.get("/customer/cryptos", response_model=List[Transaction])
async def get_customer_crypto_transactions(user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    userid=user.customer_id
    # Assuming 'crypto_id' is used to identify crypto transactions stock_id
    transactions = await collections["transactions"].find({"customer_id": userid, "stock_id": {"$eq": 0}}).to_list(length=100)
    return transactions



# @router.get("/customer-stocks", response_model=List[Cstock])
# async def get_customer_stocks(user: Customer = Depends(authutils.get_current_user)):
#     collections = await get_collections()
#     transactions = await collections["transactions"].find({"customer_id": user.customer_id}).to_list(length=None)

#     if not transactions:
#         raise HTTPException(status_code=404, detail="No transactions found for the user")

#     customer_stocks = [
#         Cstock(
#             stock_ticket=transaction["ticket"],
#             each_cost=transaction["each_cost"],
#             volume=transaction["volume"]
#         )
#         for transaction in transactions
#     ]
#     return customer_stocks

from collections import defaultdict



@router.get("/customer-stocks", response_model=List[Cstock])
async def get_customer_stocks(user: Customer = Depends(authutils.get_current_user)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"customer_id": user.customer_id,"crypto_id": {"$eq": 0}}).to_list(length=None)

    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found for the user")

    stock_aggregate = defaultdict(lambda: {'each_cost': 0, 'volume': 0})
    
    for transaction in transactions:
        ticket = transaction['ticket']
        stock_aggregate[ticket]['volume'] += transaction['volume']
        stock_aggregate[ticket]['each_cost'] = transaction['each_cost']

    customer_stocks = [
        Cstock(
            stock_ticket=ticket,
            each_cost=info['each_cost'],
            volume=info['volume']
        )
        for ticket, info in stock_aggregate.items()
    ]
    return customer_stocks

from pydantic import BaseModel, EmailStr
class CCrypto(BaseModel):
    crypto_ticket: str
    each_cost: float
    volume: int

@router.get("/customer-cryptos", response_model=List[CCrypto])
async def get_customer_cryptos(user: Customer = Depends(authutils.get_current_user)):
    collections = await get_collections()
    transactions = await collections["transactions"].find({"customer_id": user.customer_id,"stock_id": {"$eq": 0}}).to_list(length=None)

    if not transactions:
        raise HTTPException(status_code=404, detail="No crypto transactions found for the user")

    crypto_aggregate = defaultdict(lambda: {'each_cost': 0, 'volume': 0, 'count': 0})

    # Aggregate transaction details
    for transaction in transactions:
        ticket = transaction['ticket']
        crypto_aggregate[ticket]['volume'] += transaction['volume']
        crypto_aggregate[ticket]['each_cost'] += transaction['each_cost']
        crypto_aggregate[ticket]['count'] += 1

    # Calculate average cost and format the results
    customer_cryptos = [
        CCrypto(
            crypto_ticket=ticket,
            each_cost=info['each_cost'] / info['count'],
            volume=info['volume']
        ) for ticket, info in crypto_aggregate.items()
    ]

    return customer_cryptos


@router.get("/admin/", response_model=list[Transaction])
async def get_stocks(user: Customer = Depends(authutils.get_current_admin)):
    # userid=user.customer_id
    collections = await get_collections()
    transaction_data = await collections["transactions"].find().to_list(length=100)
    
    return transaction_data


@router.get("/adminpro/", response_model=list[Transactionpro])
async def get_transactions(user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transaction_data = await collections["transactions"].find().to_list(length=100)
    
    # Prepare to enrich transactions with customer and agent names
    for transaction in transaction_data:
        # Fetch the customer name
        customer = await collections["customers"].find_one({"customer_id": transaction["customer_id"]})
        transaction["customer_name"] = customer["username"] if customer else "Unknown"

        # Fetch the agent name
        agent = await collections["agents"].find_one({"agent_id": transaction["agent_id"]})
        transaction["agent_name"] = agent["name"] if agent else "Unknown"

    return [Transactionpro(**t) for t in transaction_data]



@router.get("/admin/{transcationid}", response_model=Transaction)
async def read_transaction_byid(transcationid: int, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    item = await collections["transactions"].find_one({"transaction_id": transcationid})
    if item:
        return Transaction(**item)
    raise HTTPException(status_code=404, detail="Item not found")





@router.post("/", response_model=Transaction)
async def create_stock(trancation: TransactionRequest, user: Customer = Depends(authutils.get_current_user)):
    collections = await get_collections()

    max_id_doc = await collections["transactions"].find_one(sort=[("transaction_id", -1)])
    max_id = max_id_doc['transaction_id'] + 1 if max_id_doc and 'transaction_id' in max_id_doc else 1

    transaction_data = trancation.dict(by_alias=True)
    transaction_data["transaction_id"] = max_id
    transaction_data["customer_id"] = user.customer_id  
    transaction_data["date"] = datetime.now()
    
      
    result = await collections["transactions"].insert_one(transaction_data)
    created_transaction = await collections["transactions"].find_one({"_id": result.inserted_id})
    return created_transaction

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class TransactionFilter(BaseModel):
    customer_id: Optional[int] = Field(None, description="Filter transactions by customer ID")
    stock_id: Optional[int] = Field(None, description="Filter transactions by stock ID")
    action: Optional[str] = Field(None, description="Filter transactions by action type")
    ticket: Optional[str] = Field(None, description="Filter transactions by ticket symbol")
    date: Optional[datetime] = Field(None, description="Filter transactions by date, returning those after the specified date")

@router.post("/admin/[transactions]", response_model=List[Transaction])
async def get_transactions(filters: TransactionFilter, user:  Customer= Depends(authutils.get_current_admin)):
    collections = await get_collections()
    query = {k: v for k, v in filters.dict().items() if v is not None}

    transactions = await collections["transactions"].find(query).to_list(length=100)
    if not transactions:
        # If no transactions match the filter, return all transactions
        transactions = await collections["transactions"].find().to_list(length=100)

    return transactions


@router.post("/admin", response_model=Transaction)
async def create_stock(trancation: TransactionAdminRequest, user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()

    # Validate customer and agent existence
    customer = await collections["customers"].find_one({"customer_id": trancation.customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    agent = await collections["agents"].find_one({"agent_id": trancation.agent_id})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Validate stock information
    stock = await collections["stocks"].find_one({"stock_id": trancation.stock_id})
    if not stock or stock['Company_ticker'] != trancation.ticket or stock['Closed_price'] != trancation.each_cost:
        raise HTTPException(status_code=400, detail="Stock information mismatch")

    # Proceed with creating the transaction
    max_id_doc = await collections["transactions"].find_one(sort=[("transaction_id", -1)])
    max_id = max_id_doc['transaction_id'] + 1 if max_id_doc and 'transaction_id' in max_id_doc else 1
    transaction_data = trancation.dict(by_alias=True)
    transaction_data["transaction_id"] = max_id
    transaction_data["date"] = datetime.now()
    
    result = await collections["transactions"].insert_one(transaction_data)
    created_transaction = await collections["transactions"].find_one({"_id": result.inserted_id})
    return created_transaction



@router.put("/admin/{transcationid}", response_model=Transaction)
async def update_transaction(transcationid: int, update_data: TransactionAdminRequest ,user: Customer = Depends(authutils.get_current_admin)):
    collections = await get_collections()
    transaction = await collections["transactions"].find_one({"transaction_id": transcationid})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
   
    customer = await collections["customers"].find_one({"customer_id": update_data.customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    agent = await collections["agents"].find_one({"agent_id": update_data.agent_id})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")


    stock = await collections["stocks"].find_one({"stock_id": update_data.stock_id})
    if not stock or stock['Company_ticker'] != update_data.ticket or stock['Closed_price'] != update_data.each_cost:
        raise HTTPException(status_code=400, detail="Stock information mismatch")
    updated_TRANSACTION = await collections["transactions"].find_one_and_update(
        {"transaction_id": transcationid},
        {"$set": update_data.dict(by_alias=True)},
        return_document=ReturnDocument.AFTER
    )
    if updated_TRANSACTION:
        return Transaction(**updated_TRANSACTION)
    else:
        raise HTTPException(status_code=404, detail="Stock not found")
    




from pydantic import BaseModel, EmailStr

class TransactionDeleteRequest(BaseModel):
    transaction_ids: List[int]
    
    
    

@router.delete("/admin", response_model=dict, status_code=status.HTTP_200_OK)
async def delete_transaction(delete_request: TransactionDeleteRequest ,user: Customer = Depends(authutils.get_current_admin)):
    transaction_ids = delete_request.transaction_ids
    collections = await get_collections()
    delete_result = await collections["transactions"].delete_many({"transaction_id": {"$in": transaction_ids}})

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No transactions found to delete")
    return {"message": f"{delete_result.deleted_count} transactions deleted successfully"}


# class CustomerDeleteRequest(BaseModel):
#     customer_ids: List[int]

# @router.delete("/admin", response_model=dict, status_code=status.HTTP_200_OK)
# async def delete_customers(delete_request: CustomerDeleteRequest, user: Customer = Depends(authutils.get_current_admin)):
#     customer_ids = delete_request.customer_ids
#     collections = await get_collections()
    
#     delete_result = await collections["customers"].delete_many({"customer_id": {"$in": customer_ids}})
    
#     if delete_result.deleted_count == 0:
#         raise HTTPException(status_code=404, detail="No customers found to delete")
    
#     return {"message": f"{delete_result.deleted_count} customers deleted successfully"}