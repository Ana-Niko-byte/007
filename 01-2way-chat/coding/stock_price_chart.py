# filename: stock_price_chart.py
import yfinance as yf
import matplotlib.pyplot as plt

# Get stock data for META and TESLA
meta_data = yf.Ticker("META").history(period="1mo")
tesla_data = yf.Ticker("TSLA").history(period="1mo")

# Plotting the stock price change
plt.figure(figsize=(12, 6))
plt.plot(meta_data['Close'], label='META', color='b')
plt.plot(tesla_data['Close'], label='TESLA', color='r')

plt.title('Stock Price Change - META vs TESLA')
plt.xlabel('Date')
plt.ylabel('Stock Price (USD)')
plt.legend()
plt.grid(True)
plt.show()