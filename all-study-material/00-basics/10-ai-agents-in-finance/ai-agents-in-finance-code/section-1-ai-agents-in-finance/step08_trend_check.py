"""The same plan as the agent, as plain code: is AAPL in an up- or downtrend? (no API key)"""
import yfinance as yf

prices = yf.Ticker("AAPL").history(period="3mo")["Close"]      # step 1: ~63 daily closing prices
ma20 = prices.rolling(window=20).mean()                        # step 2: 20-day moving average
today_ma, week_ago_ma = ma20.iloc[-1], ma20.iloc[-6]           # step 3: today vs 5 trading days earlier
trend = "Uptrend" if today_ma > week_ago_ma else "Downtrend"   # step 4: label it
print(f"MA20 today={today_ma:.2f}, a week ago={week_ago_ma:.2f} → {trend}")
