import pandas as pd
import numpy as np

# Set seed for reproducibility
np.random.seed(42)

# Generate 2000 business days starting from 2020-01-01
dates = pd.bdate_range(start="2020-01-01", periods=2000)

# Simulate stock prices using a random walk starting at 100.0
price = 100.0
prices = []
for _ in range(2000):
    daily_return = np.random.normal(0, 1)
    price += daily_return
    prices.append(price)

# Generate data for Open, High, Low, Close, and Volume
data = []
for i in range(2000):
    close = prices[i]
    # For the first day, use the close as the open price; otherwise, previous day's close
    open_price = prices[i-1] if i > 0 else close
    # Simulate the high as the maximum of open and close plus a small random increment
    high = max(open_price, close) + abs(np.random.normal(0, 0.5))
    # Simulate the low as the minimum of open and close minus a small random decrement
    low = min(open_price, close) - abs(np.random.normal(0, 0.5))
    volume = np.random.randint(100000, 1000000)
    data.append({
        "Date": dates[i].strftime("%Y-%m-%d"),
        "Open": round(open_price, 2),
        "High": round(high, 2),
        "Low": round(low, 2),
        "Close": round(close, 2),
        "Volume": volume
    })

# Create a DataFrame and save it as CSV
df = pd.DataFrame(data)
df.to_csv("historical_stock_data.csv", index=False)

print("historical_stock_data.csv generated with 2000 rows.")
