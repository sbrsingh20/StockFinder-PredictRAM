import streamlit as st
import pandas as pd

# Define scoring parameters
def score_indicators(row):
    score = 0
    
    # Example scoring logic
    if row['SMA_50'] > row['SMA_200']:
        score += 1  # Positive score for bullish crossover
    elif row['SMA_50'] < row['SMA_200']:
        score -= 1  # Negative score for bearish crossover

    if row['RSI'] < 30:
        score += 1  # Oversold
    elif row['RSI'] > 70:
        score -= 1  # Overbought

    if row['MACD'] > row['MACD_Signal']:
        score += 1  # Bullish MACD
    elif row['MACD'] < row['MACD_Signal']:
        score -= 1  # Bearish MACD

    return score

# Function to read data and calculate scores
def analyze_stocks(file_path):
    data = pd.read_excel(file_path)
    
    # Calculate scores
    data['Score'] = data.apply(score_indicators, axis=1)
    
    # Determine buying ranges based on stop-loss and target parameters
    for index, row in data.iterrows():
        if row['Score'] > 0:
            row['Buying Range'] = (row['Lower_BB'], row['Upper_BB'])
            row['Upper Buying Range'] = row['Upper_BB']
            row['Lower Buying Range'] = row['Lower_BB']
        else:
            row['Buying Range'] = (None, None)
            row['Upper Buying Range'] = None
            row['Lower Buying Range'] = None

    return data.sort_values(by='Score', ascending=False)

# Main function to run the app
def main():
    st.title("Stock Analysis and Trading Strategy")

    # Upload file
    uploaded_file = st.file_uploader("Choose a stocks Excel file", type=["xlsx"])

    if uploaded_file is not None:
        # Analyze stocks
        stocks_data = analyze_stocks(uploaded_file)

        # Show top 20 stocks for each trade category
        st.subheader("Top Stocks for Short Term Trade")
        st.dataframe(stocks_data[stocks_data['Score'] > 0].head(20))

        st.subheader("Top Stocks for Medium Term Trade")
        st.dataframe(stocks_data[stocks_data['Score'] > 0].head(20))

        st.subheader("Top Stocks for Long Term Trade")
        st.dataframe(stocks_data[stocks_data['Score'] > 0].head(20))

if __name__ == "__main__":
    main()
