import yfinance as yf
import pandas as pd

def get_recommendation(ticker):
    try:
        stock = yf.Ticker(ticker)
        upgrades_downgrades = stock.upgrades_downgrades
        if upgrades_downgrades is not None and not upgrades_downgrades.empty:
            return upgrades_downgrades
        else:
            return "No recommendation available"
    except Exception as e:
        print(f"Error fetching recommendation for {ticker}: {e}")
        return "Error"

def get_recommendation_summary(ticker):
    try:
        stock = yf.Ticker(ticker)
        rec_summary = stock.recommendations_summary
        if rec_summary is not None:
            return rec_summary
        else:
            return "No recommendation summary available"
    except Exception as e:
        print(f"Error fetching recommendation summary for {ticker}: {e}")
        return "Error"

def get_upgrades_downgrades(ticker):
    try:
        stock = yf.Ticker(ticker)
        upgrades_downgrades = stock.upgrades_downgrades
        if upgrades_downgrades is not None and not upgrades_downgrades.empty:
            return upgrades_downgrades
        else:
            return "No upgrades/downgrades available"
    except Exception as e:
        print(f"Error fetching upgrades/downgrades for {ticker}: {e}")
        return "Error"

def recommend_stock(ticker):
    recommendation = get_recommendation(ticker)
    recommendation_summary = get_recommendation_summary(ticker)
    upgrades_downgrades = get_upgrades_downgrades(ticker)

    if isinstance(recommendation, str) and recommendation == "Error":
        return "Unable to provide a recommendation due to an error in fetching recommendation data."
    
    if isinstance(recommendation_summary, str) and recommendation_summary == "Error":
        return "Unable to provide a recommendation due to an error in fetching recommendation summary data."
    
    if isinstance(upgrades_downgrades, str) and upgrades_downgrades == "Error":
        return "Unable to provide a recommendation due to an error in fetching upgrades/downgrades data."

    if not isinstance(recommendation, str):
        if 'ToGrade' in recommendation.columns:
            grades = recommendation['ToGrade'].value_counts()
            total_recommendations = len(recommendation)
            
            if 'Buy' in grades.index:
                buy_percentage = grades['Buy'] / total_recommendations * 100
            else:
                buy_percentage = 0
            
            if 'Sell' in grades.index:
                sell_percentage = grades['Sell'] / total_recommendations * 100
            else:
                sell_percentage = 0
            
            if 'Hold' in grades.index:
                hold_percentage = grades['Hold'] / total_recommendations * 100
            else:
                hold_percentage = 0
            
            if buy_percentage > sell_percentage and buy_percentage > hold_percentage:
                print(buy_percentage)
                print(sell_percentage)
                print(hold_percentage)
                return f"Buy (Buy: {grades.get('Buy', 0)}, Total Buy: {buy_percentage:.2f}%)"
            elif sell_percentage > buy_percentage and sell_percentage > hold_percentage:
                return f"Sell (Sell: {grades.get('Sell', 0)}, Total Sell: {sell_percentage:.2f}%)"
            else:
                return f"Hold (Hold: {grades.get('Hold', 0)}, Total Hold: {hold_percentage:.2f}%)"
        else:
            return "Unable to provide a recommendation due to missing 'ToGrade' column in the data."
    else:
        return "No recommendation available"

stock_tickers = ['AAPL', 'GOOGL', 'MSFT']

print("Stock Recommendations:")
for ticker in stock_tickers:
    print(f"Ticker: {ticker}")
    recommendation = recommend_stock(ticker)
    print(f"Recommendation: {recommendation}")
    print()