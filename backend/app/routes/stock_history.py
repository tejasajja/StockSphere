from fastapi import APIRouter, HTTPException, Request

from bson import ObjectId
from typing import List
import yfinance as yf
from app.models import StockData,Customer
from fastapi import APIRouter, HTTPException
from ..models import Agent, PyObjectId
from ..database.mongo import get_collections
from bson import ObjectId
from pymongo.collection import ReturnDocument
from app.utils import authutils
from fastapi import APIRouter, HTTPException, Request,Depends

router = APIRouter()


@router.get("/", response_model=list[StockData])
async def get_stocksdata():
    collections = await get_collections()
    stocks = await collections["stock_history"].find().to_list(length=100)
    return stocks



@router.post("/", response_model=StockData)
async def create_stockdata(stockdata: StockData,user: Customer = Depends(authutils.get_current_user)):
    collections = await get_collections()
    stockdata_dict = stockdata.dict(by_alias=True)  
    result = await collections["stock_history"].insert_one(stockdata_dict)
    created_stock = await collections["stock_history"].find_one({"_id": result.inserted_id})
    if created_stock is None:
        raise HTTPException(status_code=404, detail="The created stock data was not found")
    return StockData(**created_stock)

from pydantic import BaseModel, Field

class StockDataRangeRequest(BaseModel):
    company_ticker: str = Field(..., description="The stock ticker of the company")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    
    

from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Body
@router.post("/range", response_model=List[StockData])
async def get_stocks_data_in_range(
    request_body: StockDataRangeRequest = Body(..., description="Request body with company ticker, start date, and end date")
):
    start_date_obj = datetime.strptime(request_body.start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(request_body.end_date, '%Y-%m-%d')

    collections = await get_collections()

    query = {
        "Company_ticker": request_body.company_ticker,
        "date": {
            "$gte": start_date_obj.strftime('%Y-%m-%d'),
            "$lte": end_date_obj.strftime('%Y-%m-%d')
        }
    }
    stocks = await collections["stock_history"].find(query).sort("date", 1).to_list(length=None) 
    return stocks

@router.put("/{stock_id}", response_model=StockData)
async def update_stockdata(
    stock_id: str,
    stockdata: StockData,
    user: Customer = Depends(authutils.get_current_user)
):
    collections = await get_collections()
    updated_stock = await collections["stock_history"].find_one_and_update(
        {"_id": ObjectId(stock_id)},
        {"$set": stockdata.dict(by_alias=True)},
        return_document=ReturnDocument.AFTER
    )
    if updated_stock is None:
        raise HTTPException(status_code=404, detail="Stock data not found")
    return StockData(**updated_stock)


@router.delete("/{stock_id}")
async def delete_stockdata(
    stock_id: str,
    user: Customer = Depends(authutils.get_current_user)
):
    collections = await get_collections()
    deleted_stock = await collections["stock_history"].find_one_and_delete(
        {"_id": ObjectId(stock_id)}
    )
    if deleted_stock is None:
        raise HTTPException(status_code=404, detail="Stock data not found")
    return {"message": "Stock data deleted successfully"}