from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import numpy as np
import pandas as pd
import yfinance as yf
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import os

router = APIRouter()

class PredictionRequest(BaseModel):
    symbol: str
    date: str
    days: int  # Number of days for which predictions are required

def fetch_stock_data(symbol, start_date, end_date):
    """Fetches historical stock data from Yahoo Finance."""
    df = yf.download(symbol, start=start_date, end=end_date)
    return df['Close']

def prepare_data(symbol, end_date):
    """Pre-process the data"""
    start_date = pd.to_datetime(end_date) - pd.Timedelta(days=90)
    data = fetch_stock_data(symbol, start_date.strftime('%Y-%m-%d'), end_date)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(np.array(data).reshape(-1, 1))
    return scaled_data[-60:].reshape(1, 60, 1), scaler

@router.post("/predict/")
async def predict(request: PredictionRequest):
    symbol = request.symbol
    end_date = request.date
    days = request.days
    model_path = os.path.abspath(os.path.join('app/ML/ML-models', symbol, f'{symbol}-model.h5'))
    print("Absolute model path:", model_path)

    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail="Model not found")
    
    try:
        model = load_model(model_path)
        scaled_data, scaler = prepare_data(symbol, end_date)
        predictions = []
        prediction_dates = []  
        current_date = pd.to_datetime(end_date)
        
        for i in range(days):  # Use the user-specified number of days
            pred = model.predict(scaled_data)
            scaled_data = np.append(scaled_data.flatten()[1:], pred).reshape(1, 60, 1)
            predictions.append(scaler.inverse_transform(pred).flatten()[0].item())
            current_date += pd.Timedelta(days=1)
            prediction_dates.append(current_date.strftime('%Y-%m-%d'))
        
        prediction_result = [{"date": date, "Close": prediction} for date, prediction in zip(prediction_dates, predictions)]
        return prediction_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
