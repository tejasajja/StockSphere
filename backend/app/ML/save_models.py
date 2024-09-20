import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib 
import ta
import os  

def fetch_data(symbol, start_date, end_date):
    """Fetch historical data for a symbol."""
    df = yf.download(symbol, start=start_date, end=end_date)
    df['Symbol'] = symbol
    df.index = pd.to_datetime(df.index)
    return df

def add_technical_indicators(data):
    """Add technical indicators to the data."""
    data = ta.add_all_ta_features(
        data, open="Open", high="High", low="Low", close="Close", volume="Volume",
        fillna=True)
    return data

def preprocess_and_feature_engineer(data):
    """Preprocess and feature engineer the data."""
    scaler = StandardScaler()
    features = [col for col in data.columns if 'volatility' in col or 'trend' in col or 'momentum' in col]
    X = scaler.fit_transform(data[features])
    y = data['Close']
    return X, y

def train_and_save_model(symbol, start_date, end_date, filename):
    data = fetch_data(symbol, start_date, end_date)
    data = add_technical_indicators(data)
    X, y = preprocess_and_feature_engineer(data)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

    model = LinearRegression()
    model.fit(X_train, y_train)

    os.makedirs('ML-models', exist_ok=True)
    model_path = os.path.join('ML-models', filename)
    joblib.dump(model, model_path)
    predictions = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    print(f"Model trained and saved for {symbol} at {model_path}. RMSE: {rmse}")

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
    for symbol in symbols:
        train_and_save_model(symbol, start_date, end_date, f'{symbol}-model.pkl')
