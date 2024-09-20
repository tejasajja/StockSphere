from fastapi import FastAPI, HTTPException
import yfinance as yf
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from bson import ObjectId
import pandas as pd
from app.database.mongo import get_collections
from app.routes.schemas import CreateCryptoRequest
from app.routes.cryptocurrencies import create_crypto
from datetime import datetime, timedelta
from app.utils import authutils
from fastapi import APIRouter, Request, Depends
from app.models import CryptoData
app = FastAPI()

MONGO_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGO_URL)
database = client["stocksphere"]
crypto_collection = database["cryptocurrencies"]
crypto_history_collection = database["crypto_history"]

async def push_crypto(crypto: CreateCryptoRequest):
    collections = await get_collections()

    max_id_doc = await collections["cryptocurrencies"].find_one(sort=[("crypto_id", -1)])
    max_id = max_id_doc['crypto_id'] + 1 if max_id_doc and 'crypto_id' in max_id_doc else 1

    crypto_data = crypto.dict(by_alias=True)
    crypto_data["crypto_id"] = max_id

    result = await collections["cryptocurrencies"].insert_one(crypto_data)
    created_crypto = await collections["cryptocurrencies"].find_one({"_id": result.inserted_id})
    return created_crypto

async def push_cryptodata(cryptodata: CryptoData):
    collections = await get_collections()
    cryptodata_dict = cryptodata.dict(by_alias=True)
    result = await collections["crypto_history"].insert_one(cryptodata_dict)
    created_crypto = await collections["crypto_history"].find_one({"_id": result.inserted_id})
    if created_crypto is None:
        raise HTTPException(status_code=404, detail="The created crypto data was not found")
    return CryptoData(**created_crypto)

# List of cryptocurrency symbols
crypto_symbols = [
    'BTC-USD', 'ETH-USD', 'XRP-USD', 'LTC-USD', 'BCH-USD',
    'ADA-USD', 'DOT-USD', 'LINK-USD', 'XLM-USD', 'BNB-USD',
    'USDT-USD', 'SOL-USD', 'DOGE-USD', 'USDC-USD', 'UNI-USD',
    'MATIC-USD', 'AVAX-USD', 'ALGO-USD', 'TRX-USD', 'ETC-USD',
    'XMR-USD', 'EOS-USD', 'XTZ-USD', 'NEO-USD', 'FTT-USD',
    'SUSHI-USD', 'ATOM-USD', 'VET-USD', 'FIL-USD', 'AAVE-USD',
    'LUNA1-USD', 'KSM-USD', 'COMP-USD', 'ZEC-USD', 'MKR-USD',
    'SNX-USD', 'DASH-USD', 'DCR-USD', 'MANA-USD', 'ZIL-USD',
    'ENJ-USD', 'CHZ-USD', 'QTUM-USD', 'BAT-USD', 'NANO-USD',
    'WAVES-USD', 'ICX-USD', 'LRC-USD', 'ONT-USD', 'ONE-USD'
]

async def fetch_and_update_crypto_data():
    
    
    for symbol in crypto_symbols:
        try:
            crypto = yf.Ticker(symbol)
            info = crypto.info

            if await crypto_collection.count_documents({'Symbol': info['symbol']}) == 0:
                crypto_data = CreateCryptoRequest(
                    Name=info['name'],
                    Symbol=info['symbol'],
                    Last_Close=info['previousClose'],
                    Market_Cap=info.get('marketCap'),
                    Volume_24h=info.get('volume24Hr'),
                    Circulating_Supply=info.get('circulatingSupply')
                )
                await push_crypto(crypto=crypto_data)
        except Exception as e:
            print(f"Error updating crypto {symbol}: {e}")

async def fetch_and_store_historical_data():
    
    today = datetime.today().strftime('%Y-%m-%d')
    if await crypto_history_collection.count_documents({}) > 0:
        print("The collection already contains data. No action taken.")
        pass
    else:
        for symbol in crypto_symbols:
            try:
                hist = yf.download(symbol, start='2023-01-01', end=today)
                if not hist.empty:
                    hist.reset_index(inplace=True)
                    records = hist.to_dict('records')
                    for record in records:
                        record['Symbol'] = symbol
                        record['date'] = str(record['Date']).split(" ")[0]
                        del record['Date']
                    await crypto_history_collection.insert_many(records)
            except Exception as e:
                print(f"Error downloading historical data for {symbol}: {e}")

