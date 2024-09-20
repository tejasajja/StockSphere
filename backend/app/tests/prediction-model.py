import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
import ta  # Technical Analysis library for financial indicators

def fetch_data(symbols, start_date, end_date):
    """Fetch historical data for a list of symbols."""
    dfs = []
    for symbol in symbols:
        df = yf.download(symbol, start=start_date, end=end_date)
        df['Symbol'] = symbol
        dfs.append(df)
    combined_data = pd.concat(dfs)
    combined_data.index = pd.to_datetime(combined_data.index)
    return combined_data

def add_technical_indicators(data):
    """Add technical indicators to the data using the TA library."""
    data = data.copy()
    data = ta.add_all_ta_features(
        data,
        open="Open", high="High", low="Low", close="Close", volume="Volume",
        fillna=True
    )
    return data

def preprocess_and_feature_engineer(data):
    """Preprocess and feature engineer the data."""
    data = add_technical_indicators(data)
    scaler = StandardScaler()
    features = [col for col in data.columns if 'volatility' in col or 'trend' in col or 'momentum' in col]
    X = scaler.fit_transform(data[features])
    y = data['Close']
    return X, y, data.index  # Return the index for date handling

def plot_predictions(dates, actual, predicted, symbol, pdf):
    """Plot actual vs predicted stock prices and save to a PDF file."""
    plt.figure(figsize=(14, 7))
    plt.plot(dates, actual, 'bo-', label='Actual Prices', linewidth=2, markersize=4)
    plt.plot(dates, predicted, 'r--', label='Predicted Prices', linewidth=2)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    plt.gcf().autofmt_xdate()
    plt.title(f'Actual vs Predicted Prices for {symbol}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.savefig(pdf, format='pdf')
    plt.close()

def main():
    symbols = [
    'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'BRK-B', 'JNJ', 'V', 'PG', 'JPM',
    'TSLA', 'NVDA', 'DIS', 'NFLX', 'PFE', 'KO', 'NKE', 'XOM', 'CVX', 'CSCO',
    'INTC', 'WMT', 'T', 'VZ', 'UNH', 'HD', 'MCD', 'BA', 'MMM', 'CAT',
    'GS', 'IBM', 'MRK', 'GE', 'F', 'GM', 'ADBE', 'CRM', 'ORCL', 'ABT',
    'BAC', 'C', 'GILD', 'LLY', 'MDT', 'AMGN', 'MO', 'PEP', 'TMO', 'DHR'
]
    start_date = '2010-01-01'
    end_date = '2024-01-01'
    data = fetch_data(symbols, start_date, end_date)

    with PdfPages('predictions.pdf') as pdf:
        for symbol in symbols:
            print(f"Processing {symbol}...")
            data_symbol = data[data['Symbol'] == symbol]
            X, y, dates = preprocess_and_feature_engineer(data_symbol)
            
            # Splitting while preserving the dates for test data
            indices = np.arange(X.shape[0])
            X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
                X, y, indices, test_size=0.2, random_state=42, shuffle=False)
            dates_train, dates_test = dates[idx_train], dates[idx_test]

            model = LinearRegression()
            model.fit(X_train, y_train)
            predictions = model.predict(X_test)

            rmse_value = np.sqrt(mean_squared_error(y_test, predictions))
            print(f'RMSE for {symbol} in 2023: {rmse_value:.2f}')

            plot_predictions(dates_test, y_test, predictions, symbol, pdf)

if __name__ == '__main__':
    main()