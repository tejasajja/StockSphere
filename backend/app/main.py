from fastapi import FastAPI
from app.routes import agents, customers, stocks, stock_history, transactions, crypto_history, cryptocurrencies, queries
from app.ML import predict
from app.database.mongo import MongoDB
from fastapi.middleware.cors import CORSMiddleware
from app.utils import yahoo_finance, yahoo_finance_crypto
from app.routes import auth
from app.routes import auth
from datetime import datetime
import asyncio

app = FastAPI()


async def update_recent_data():
    while True:
        current_date = datetime.now()
        await yahoo_finance.fetch_and_update_stock_data()
        await yahoo_finance.fetch_and_store_historical_data()
        await yahoo_finance_crypto.fetch_and_update_crypto_data()
        await yahoo_finance_crypto.fetch_and_store_historical_data()
        await asyncio.sleep(300)  


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_recent_data())


app.include_router(agents.router, prefix="/api/agents", tags=["Agents"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["Stocks"])
app.include_router(stock_history.router, prefix="/api/stock-history", tags=["Stock-History"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(cryptocurrencies.router, prefix="/api/cryptocurrencies", tags=["Cryptocurrencies"])
app.include_router(crypto_history.router, prefix="/api/crypto_history", tags=["Crypto_History"])
app.include_router(queries.router, prefix="/api/queries", tags=["Queries"])
app.include_router(predict.router, prefix="/api/predict", tags=["ML-Model"])


app.add_middleware(
    CORSMiddleware,
     allow_origins=['http://localhost:3000','http://localhost:5173'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, tags=['Auth'], prefix='/api/auth')


@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to Stocks & Crypto Management System"}

# @app.on_event("startup")
# async def startup_event():
#     app.state.mongo_client = MongoDB.get_client()
#     app.state.mongo_db = app.state.mongo_client.stocksphere
#     app.state.mongo_collections = {
#         "agents": app.state.mongo_db.agents,
#         "customers": app.state.mongo_db.customers,
#         "stocks": app.state.mongo_db.stocks,
#         "stock_history": app.state.mongo_db.stock_history,
#         "transactions": app.state.mongo_db.transactions,
#     }

# @app.on_event("shutdown")
# async def shutdown_event():
#     app.state.mongo_client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    
    
    
#-------------------------------------------------------------------------------Auth
