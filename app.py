import streamlit as st
import yfinance as yf
import pandas as pd

# Define the trading strategy parameters
TRADE_STRATEGY = {
    "Short Term": {"days": 30, "stop_loss": 0.03, "min_return": 0.05},
    "Medium Term": {"days": 180, "stop_loss": 0.04, "min_return": 0.10},
    "Long Term": {"days": 365, "stop_loss": 0.05, "min_return": 0.15}
}

# Nifty 20 stocks list
nifty_20_stocks = [
    'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
    'HDFC.NS', 'ICICIBANK.NS', 'KOTAKBANK.NS', 'LT.NS', 'BAJFINANCE.NS',
    'TITAN.NS', 'SBI.NS', 'ASIANPAINT.NS', 'HCLTECH.NS', 'WIPRO.NS',
    'MARUTI.NS', 'BHARTIARTL.NS', 'SUNPHARMA.NS', 'ITC.NS', 'ULTRACEMCO.NS'
]

# Function to fetch stocks
def fetch_stocks():
    results = []
    for stock in nifty_20_stocks:
        data = yf.Ticker(stock).history(period='1y')
        if not data.empty:
            current_price = data['Close'].iloc[-1]
            results.append((stock, current_price))
        else:
            st.warning(f"No data for {stock}")

    return results

# Calculate target and stop loss prices
def calculate_trade_parameters(stock_data, strategy):
    results = []
    for stock, current_price in stock_data:
        stop_loss = current_price * (1 - strategy['stop_loss'])
        target_price = current_price * (1 + strategy['min_return'])
        results.append({
            "Stock": stock,
            "Current Price": current_price,
            "Stop Loss": stop_loss,
            "Target Price": target_price
        })
    return results

# Main function to run the app
def main():
    st.title("Trade Strategy Updates")

    # Fetch stock data
    stock_data = fetch_stocks()

    # Display results for each trade strategy
    for strategy_name, strategy_params in TRADE_STRATEGY.items():
        st.subheader(strategy_name)
        trade_results = calculate_trade_parameters(stock_data, strategy_params)
        df = pd.DataFrame(trade_results)
        st.dataframe(df)

if __name__ == "__main__":
    main()
