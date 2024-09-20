from fastapi import FastAPI

app = FastAPI()

from app.routes import agents ,customers, stocks, stock_history, transactions

app.include_router(agents.router)
app.include_router(customers.router)
app.include_router(stocks.router)
app.include_router(stock_history.router)
app.include_router(transactions.router)