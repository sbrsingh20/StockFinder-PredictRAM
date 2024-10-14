import streamlit as st
import yfinance as yf
import pandas as pd
from ta import add_all_ta_features

# Define the trading strategy parameters
TRADE_STRATEGY = {
    "Short Term": {"days": 30, "stop_loss": 0.03, "min_return": 0.05},
    "Medium Term": {"days": 180, "stop_loss": 0.04, "min_return": 0.10},
    "Long Term": {"days": 365, "stop_loss": 0.05, "min_return": 0.15}
}

# Function to fetch stock data from an Excel file
def read_stock_data(file_path):
    df = pd.read_excel(file_path)
    return df

# Function to fetch additional stock data from Yahoo Finance
def fetch_additional_data(stock):
    data = yf.Ticker(stock).history(period='1y')
    if not data.empty:
        return data
    else:
        st.warning(f"No data for {stock}")
        return None

# Function to calculate the score for each stock
def calculate_scores(df):
    scores = []
    for index, row in df.iterrows():
        score = 0
        # Example scoring based on indicators
        score += 1 if row['SMA_50'] > row['SMA_200'] else 0  # Bullish
        score += 1 if row['RSI'] < 30 else 0  # Oversold
        score += 1 if row['MACD'] > row['MACD_Signal'] else 0  # Bullish MACD
        scores.append((row['Stock'], score))
    return scores

# Calculate trade parameters
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

    # Load stock data from Excel
    stock_df = read_stock_data("stocks.xlsx")
    stock_df.set_index('Stock', inplace=True)

    # Fetch additional data and calculate indicators
    for stock in stock_df.index:
        historical_data = fetch_additional_data(stock)
        if historical_data is not None:
            historical_data = add_all_ta_features(historical_data, open="Open", high="High", low="Low", close="Close", volume="Volume", fillna=True)
            stock_df.loc[stock, 'SMA_50'] = historical_data['SMA_50'].iloc[-1]
            stock_df.loc[stock, 'SMA_200'] = historical_data['SMA_200'].iloc[-1]
            stock_df.loc[stock, 'EMA_12'] = historical_data['EMA_12'].iloc[-1]
            stock_df.loc[stock, 'EMA_26'] = historical_data['EMA_26'].iloc[-1]
            stock_df.loc[stock, 'RSI'] = historical_data['RSI'].iloc[-1]
            stock_df.loc[stock, 'MACD'] = historical_data['MACD'].iloc[-1]
            stock_df.loc[stock, 'MACD_Signal'] = historical_data['MACD_Signal'].iloc[-1]
            stock_df.loc[stock, 'MACD_Hist'] = historical_data['MACD_Hist'].iloc[-1]
            stock_df.loc[stock, 'Upper_BB'] = historical_data['BB_High'].iloc[-1]
            stock_df.loc[stock, 'Lower_BB'] = historical_data['BB_Low'].iloc[-1]
            stock_df.loc[stock, 'Volatility (%)'] = historical_data['volatility'].iloc[-1] * 100
            stock_df.loc[stock, 'Beta'] = historical_data['beta'].iloc[-1]  # Assuming this column is calculated

    # Calculate scores
    stock_scores = calculate_scores(stock_df)
    stock_scores_df = pd.DataFrame(stock_scores, columns=['Stock', 'Score'])
    top_stocks = stock_scores_df.sort_values(by='Score', ascending=False)

    # Display results for each trade strategy
    for strategy_name, strategy_params in TRADE_STRATEGY.items():
        st.subheader(strategy_name)
        trade_results = calculate_trade_parameters(top_stocks.head(20).values, strategy_params)
        df = pd.DataFrame(trade_results)
        st.dataframe(df)

if __name__ == "__main__":
    main()
