# ai_analysis/analysis.py
import pandas as pd
from textblob import TextBlob

def analyze_historical_data():
    # Load historical stock data from a CSV or external API
    stock_data = pd.read_csv("data/historical_stock_data.csv")
    
    # Example: Compute a 50-day moving average for trend analysis
    stock_data['MA50'] = stock_data['Close'].rolling(window=50).mean()
    latest_ma50 = stock_data['MA50'].iloc[-1]
    
    return latest_ma50

def analyze_news_sentiment():
    # In a real-world scenario, fetch news headlines from an API
    news_headlines = [
        "Market shows bullish trends as earnings beat expectations",
        "Economic slowdown worries investors amid geopolitical tensions"
    ]
    
    sentiments = [TextBlob(headline).sentiment.polarity for headline in news_headlines]
    average_sentiment = sum(sentiments) / len(sentiments)
    
    return average_sentiment

def run_market_trend_analysis():
    # Get analysis from various sources
    trend_indicator = analyze_historical_data()
    news_sentiment = analyze_news_sentiment()
    
    # Combine analysis into a result dictionary
    results = {
        "trend_indicator": trend_indicator,
        "news_sentiment": news_sentiment,
        "investment_suggestion": "Buy" if trend_indicator > 100 and news_sentiment > 0 else "Sell"
    }
    
    return results
