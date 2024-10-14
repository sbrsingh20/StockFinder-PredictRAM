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
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        st.error(f"Error reading the Excel file: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error

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
        score += 1 if row['EMA_12'] > row['EMA_26'] else 0  # Bullish EMA
        score += 1 if row['RSI'] < 30 else 0  # Oversold condition
        score += 1 if row['MACD'] > row['MACD_Signal'] else 0  # Bullish MACD
        scores.append((row.name, score))  # Use row name for the stock
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
    if stock_df.empty:
        st.error("No stock data available. Please check your Excel file.")
        return

    if 'Stock' not in stock_df.columns:
        st.error("The 'Stock' column is missing in the Excel file.")
        return

    stock_df.set_index('Stock', inplace=True)

    # Fetch additional data and calculate indicators
    for stock in stock_df.index:
        historical_data = fetch_additional_data(stock)
        if historical_data is not None:
            historical_data = add_all_ta_features(
                historical_data, open="Open", high="High", low="Low", close="Close", volume="Volume", fillna=True
            )

            # Check if the necessary columns are in the historical_data DataFrame
            required_columns = ['ema_indicator_12', 'ema_indicator_26', 'rsi', 'macd', 'macd_signal', 'macd_diff', 'bb_hband', 'bb_lband']
            for column in required_columns:
                if column not in historical_data.columns:
                    st.warning(f"Missing column: {column} for stock {stock}.")
                    return

            # Store the calculated indicators
            stock_df.loc[stock, 'EMA_12'] = historical_data['ema_indicator_12'].iloc[-1]
            stock_df.loc[stock, 'EMA_26'] = historical_data['ema_indicator_26'].iloc[-1]
            stock_df.loc[stock, 'RSI'] = historical_data['rsi'].iloc[-1]
            stock_df.loc[stock, 'MACD'] = historical_data['macd'].iloc[-1]
            stock_df.loc[stock, 'MACD_Signal'] = historical_data['macd_signal'].iloc[-1]
            stock_df.loc[stock, 'MACD_Hist'] = historical_data['macd_diff'].iloc[-1]
            stock_df.loc[stock, 'Upper_BB'] = historical_data['bb_hband'].iloc[-1]
            stock_df.loc[stock, 'Lower_BB'] = historical_data['bb_lband'].iloc[-1]
            stock_df.loc[stock, 'Volatility (%)'] = historical_data['volatility'].iloc[-1] * 100
            stock_df.loc[stock, 'Beta'] = 1.0  # Default value for Beta

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
