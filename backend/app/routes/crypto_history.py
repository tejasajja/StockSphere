from fastapi import APIRouter, HTTPException, Request
from bson import ObjectId
from typing import List
import yfinance as yf
from app.models import CryptoData, Customer
from app.database.mongo import get_collections
from pymongo.collection import ReturnDocument
from app.utils import authutils
from fastapi import Depends

from pydantic import BaseModel, Field
router = APIRouter()

@router.get("/", response_model=List[CryptoData])
async def get_cryptos_data():
    collections = await get_collections()
    cryptos = await collections["crypto_history"].find().to_list(length=100)
    return cryptos

@router.post("/", response_model=CryptoData)
async def create_crypto_data(cryptodata: CryptoData, user: Customer = Depends(authutils.get_current_user)):
    collections = await get_collections()
    cryptodata_dict = cryptodata.dict(by_alias=True)
    result = await collections["crypto_history"].insert_one(cryptodata_dict)
    created_crypto = await collections["crypto_history"].find_one({"_id": result.inserted_id})
    if created_crypto is None:
        raise HTTPException(status_code=404, detail="The created crypto data was not found")
    return CryptoData(**created_crypto)


class StockDataRangeRequest(BaseModel):
    company_ticker: str = Field(..., description="The stock ticker of the company")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    
    

from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Body
@router.post("/range", response_model=List[CryptoData])
async def get_stocks_data_in_range(
    request_body: StockDataRangeRequest = Body(..., description="Request body with company ticker, start date, and end date")
):
    start_date_obj = datetime.strptime(request_body.start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(request_body.end_date, '%Y-%m-%d')

    collections = await get_collections()

    query = {
        "Symbol": request_body.company_ticker,
        "date": {
            "$gte": start_date_obj.strftime('%Y-%m-%d'),
            "$lte": end_date_obj.strftime('%Y-%m-%d')
        }
    }
    stocks = await collections["crypto_history"].find(query).sort("date", 1).to_list(length=None) 
    return stocks


@router.put("/{crypto_id}", response_model=CryptoData)
async def update_crypto_data(
    crypto_id: str,
    cryptodata: CryptoData,
    user: Customer = Depends(authutils.get_current_user)
):
    collections = await get_collections()
    updated_crypto = await collections["crypto_history"].find_one_and_update(
        {"_id": ObjectId(crypto_id)},
        {"$set": cryptodata.dict(by_alias=True)},
        return_document=ReturnDocument.AFTER
    )
    if updated_crypto is None:
        raise HTTPException(status_code=404, detail="Crypto data not found")
    return CryptoData(**updated_crypto)


@router.delete("/{crypto_id}")
async def delete_crypto_data(
    crypto_id: str,
    user: Customer = Depends(authutils.get_current_user)
):
    collections = await get_collections()
    deleted_crypto = await collections["crypto_history"].find_one_and_delete(
        {"_id": ObjectId(crypto_id)}
    )
    if deleted_crypto is None:
        raise HTTPException(status_code=404, detail="Crypto data not found")
    return {"message": "Crypto data deleted successfully"}