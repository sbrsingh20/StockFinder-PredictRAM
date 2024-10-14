import streamlit as st
import pandas as pd

# Define scoring parameters
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
        score += 1  # Oversold
    elif row['RSI'] > 70:
        score -= 1  # Overbought

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

    # Determine buying ranges based on indicators
    data['Buying Range'] = data.apply(lambda row: (row['Lower_BB'], row['Upper_BB']) if row['Score'] > 0 else (None, None), axis=1)
    data['Upper Buying Range'] = data['Upper_BB']
    data['Lower Buying Range'] = data['Lower_BB']

    return data.sort_values(by='Score', ascending=False)

# Main function to run the app
def main():
    st.title("Stock Analysis and Trading Strategy")

    # Upload file
    uploaded_file = st.file_uploader("Choose a stocks Excel file", type=["xlsx"])

    if uploaded_file is not None:
        # Analyze stocks
        stocks_data = analyze_stocks(uploaded_file)

        # Check if any data is available
        if not stocks_data.empty:
            # Show top 20 stocks for each trade category
            st.subheader("Top Stocks for Short Term Trade")
            st.dataframe(stocks_data.head(20))

            st.subheader("Top Stocks for Medium Term Trade")
            st.dataframe(stocks_data.head(20))

            st.subheader("Top Stocks for Long Term Trade")
            st.dataframe(stocks_data.head(20))

if __name__ == "__main__":
    main()
