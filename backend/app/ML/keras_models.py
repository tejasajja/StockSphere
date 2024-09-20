import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.models import load_model
import os

def fetch_stock_data(symbol, start_date, end_date):
    """Fetches historical stock data from Yahoo Finance."""
    df = yf.download(symbol, start=start_date, end=end_date)
    return df['Close']

def create_dataset(data, time_step=1):
    X, y = [], []
    for i in range(len(data) - time_step - 1):
        a = data[i:(i + time_step), 0]
        X.append(a)
        y.append(data[i + time_step, 0])
    return np.array(X), np.array(y)

def prepare_data(symbol):
    data = fetch_stock_data(symbol, '2010-01-01', '2020-01-01')
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(np.array(data).reshape(-1, 1))
    time_step = 100
    X_train, y_train = create_dataset(scaled_data, time_step)
    X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
    return X_train, y_train, scaler

def build_and_train_model(X_train, y_train, symbol):
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(100, 1)))
    model.add(LSTM(50, return_sequences=True))
    model.add(LSTM(50))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(X_train, y_train, epochs=100, batch_size=64, verbose=1)
    model_dir = f'ML-models/{symbol}'
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, f'{symbol}-model.h5')
    model.save(model_path)
    return model, model_path

def predict_next_10_days(symbol, model_path='LSTM_model.h5'):
    data = fetch_stock_data(symbol, '2020-01-02', '2024-04-23')
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(np.array(data).reshape(-1, 1))
    X_test, _ = create_dataset(scaled_data, 100)
    X_test = X_test[-1].reshape(1, 100, 1)
    model = load_model(model_path)
    predictions = []
    for _ in range(10):
        pred = model.predict(X_test)[0][0]
        predictions.append(pred)
        X_test = np.append(X_test[0], pred)[1:].reshape(1, 100, 1)
    
    return scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()

def train_and_save_for_all_symbols(symbols, start_date, end_date):
    for symbol in symbols:
        print(f"Processing {symbol}...")
        data = fetch_stock_data(symbol, start_date, end_date)
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(np.array(data).reshape(-1, 1))
        time_step = 60
        X_train, y_train = create_dataset(scaled_data, time_step)
        X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
        model, model_path = build_and_train_model(X_train, y_train, symbol)
        print(f"Model for {symbol} saved at {model_path}")

if __name__ == '__main__':
    symbols = [
        'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'BRK-B', 'JNJ', 'V', 'PG', 'JPM',
        'TSLA', 'NVDA', 'DIS', 'NFLX', 'PFE', 'KO', 'NKE', 'XOM', 'CVX', 'CSCO',
        'INTC', 'WMT', 'T', 'VZ', 'UNH', 'HD', 'MCD', 'BA', 'MMM', 'CAT',
        'GS', 'IBM', 'MRK', 'GE', 'F', 'GM', 'ADBE', 'CRM', 'ORCL', 'ABT',
        'BAC', 'C', 'GILD', 'LLY', 'MDT', 'AMGN', 'MO', 'PEP', 'TMO', 'DHR'
    ]
    start_date = '2010-01-01'
    end_date = '2020-01-01'
    train_and_save_for_all_symbols(symbols, start_date, end_date)
