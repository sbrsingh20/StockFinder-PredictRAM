import streamlit as st
import pandas as pd

# Define scoring function based on technical indicators
def score_indicators(row):
    score = 0

    # Check for NaN values in critical indicators
    if pd.isna(row['SMA_50']) or pd.isna(row['SMA_200']):
        return score  # Skip scoring if SMA indicators are NaN

    if row['SMA_50'] > row['SMA_200']:
        score += 1  # Positive score for bullish crossover
    elif row['SMA_50'] < row['SMA_200']:
        score -= 1  # Negative score for bearish crossover

    if pd.isna(row['RSI']):
        return score  # Skip if RSI is NaN

    if row['RSI'] < 30:
        score += 1  # Oversold condition
    elif row['RSI'] > 70:
        score -= 1  # Overbought condition

    if pd.isna(row['MACD']) or pd.isna(row['MACD_Signal']):
        return score  # Skip if MACD indicators are NaN

    if row['MACD'] > row['MACD_Signal']:
        score += 1  # Bullish MACD
    elif row['MACD'] < row['MACD_Signal']:
        score -= 1  # Bearish MACD

    return score

# Function to read data and calculate scores
def analyze_stocks(file_path):
    data = pd.read_excel(file_path)

    # Check for required columns
    required_columns = [
        'SMA_50', 'SMA_200', 'EMA_12', 'EMA_26', 'RSI',
        'MACD', 'MACD_Signal', 'MACD_Hist', 'Upper_BB',
        'Lower_BB', 'Volatility (%)', 'Beta'
    ]
    
    missing_columns = [col for col in required_columns if col not in data.columns]
    if missing_columns:
        st.error(f"Missing columns in the Excel file: {', '.join(missing_columns)}")
        return pd.DataFrame()  # Return an empty DataFrame if columns are missing

    # Calculate scores
    data['Score'] = data.apply(score_indicators, axis=1)

    # Separate stocks into categories based on score (positive scores are good)
    short_term_stocks = data[data['Score'] > 0].sort_values(by='Score', ascending=False).head(20)
    medium_term_stocks = data[data['Score'] > 0].sort_values(by='Score', ascending=False).head(20)
    long_term_stocks = data[data['Score'] > 0].sort_values(by='Score', ascending=False).head(20)

    return short_term_stocks, medium_term_stocks, long_term_stocks

# Main function to run the app
def main():
    st.title("Stock Analysis and Trading Strategy")

    # Upload file
    uploaded_file = st.file_uploader("Choose a stocks Excel file", type=["xlsx"])

    if uploaded_file is not None:
        # Analyze stocks
        short_term_stocks, medium_term_stocks, long_term_stocks = analyze_stocks(uploaded_file)

        # Check if any data is available
        if not short_term_stocks.empty:
            st.subheader("Top 20 Stocks for Short Term Trade")
            st.dataframe(short_term_stocks)

        if not medium_term_stocks.empty:
            st.subheader("Top 20 Stocks for Medium Term Trade")
            st.dataframe(medium_term_stocks)

        if not long_term_stocks.empty:
            st.subheader("Top 20 Stocks for Long Term Trade")
            st.dataframe(long_term_stocks)

if __name__ == "__main__":
    main()
