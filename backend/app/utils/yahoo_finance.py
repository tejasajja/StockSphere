from fastapi import FastAPI
import yfinance as yf
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from bson import ObjectId
import pandas as pd
from app.database.mongo import get_collections
from app.routes.schemas import CreateStockRequest
from ..routes.stocks import create_stock
# from ..routes.stock_history import create_stockdata
from datetime import datetime, timedelta
from app.utils import authutils
from fastapi import APIRouter, HTTPException, Request,Depends
from app.models import StockData
app = FastAPI()

MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
database = client["stocksphere"]
stocks_collection = database["stocks"]
stock_history_collection = database["stock_history"]

async def push_stock(stock: CreateStockRequest):
    collections = await get_collections()

    
    max_id_doc = await collections["stocks"].find_one(sort=[("stock_id", -1)])
    max_id = max_id_doc['stock_id'] + 1 if max_id_doc and 'stock_id' in max_id_doc else 1

    stock_data = stock.dict(by_alias=True)
    stock_data["stock_id"] = max_id


    result = await collections["stocks"].insert_one(stock_data)
    created_stock = await collections["stocks"].find_one({"_id": result.inserted_id})
    return created_stock

async def push_stockdata(stockdata: StockData):
    collections = await get_collections()
    stockdata_dict = stockdata.dict(by_alias=True)  
    result = await collections["stock_history"].insert_one(stockdata_dict)
    created_stock = await collections["stock_history"].find_one({"_id": result.inserted_id})
    if created_stock is None:
        raise HTTPException(status_code=404, detail="The created stock data was not found")
    return StockData(**created_stock)



ticker_symbols = [
    'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'BRK-B', 'JNJ', 'V', 'PG', 'JPM',
    'TSLA', 'NVDA', 'DIS', 'NFLX', 'PFE', 'KO', 'NKE', 'XOM', 'CVX', 'CSCO',
    'INTC', 'WMT', 'T', 'VZ', 'UNH', 'HD', 'MCD', 'BA', 'MMM', 'CAT',
    'GS', 'IBM', 'MRK', 'GE', 'F', 'GM', 'ADBE', 'CRM', 'ORCL', 'ABT',
    'BAC', 'C', 'GILD', 'LLY', 'MDT', 'AMGN', 'MO', 'PEP', 'TMO', 'DHR'
]

async def fetch_and_update_stock_data():
    for symbol in ticker_symbols:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info

            if await stocks_collection.count_documents({'Company_ticker': info['symbol']}) == 0:
                stock_data = CreateStockRequest(
                    Company_name=info['longName'],
                    Company_ticker=info['symbol'],
                    Closed_price=info['previousClose'],
                    Company_info=info['longBusinessSummary'],
                    Company_PE=info.get('trailingPE', None),
                    Company_cash_flow=info.get('operatingCashflow', None),
                    Company_dividend=info.get('dividendRate', None)
                )
                await push_stock(stock=stock_data)
        except Exception as e:
            print(f"Error updating stock {symbol}: {e}")




async def fetch_and_store_historical_data():
    today = datetime.today().strftime('%Y-%m-%d')
    
    if await stock_history_collection.count_documents({}) > 0:
        print("The collection already contains data. No action taken.")
        pass
    else:
        
        for symbol in ticker_symbols:
            try:
                hist = yf.download(symbol, start='2023-01-01', end=today)

                if not hist.empty:
                    hist.reset_index(inplace=True)
                    records = hist.to_dict('records')
                    for record in records:
                        record['Company_ticker'] = symbol
                        record['date'] = str(record['Date'])
                        record['date']=record['date'].split(" ")[0]
                        del record['Date'] 

                    await stock_history_collection.insert_many(records)
            except Exception as e:
                print(f"Error updating intraday data for {symbol}: {e}")


