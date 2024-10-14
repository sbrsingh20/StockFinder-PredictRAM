import streamlit as st
import pandas as pd
import yfinance as yf
import ta

# Function to fetch stock indicators
def fetch_indicators(stock):
    ticker = yf.Ticker(stock)
    data = ticker.history(period="1y")

    # Calculate indicators using the ta library
    data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
    macd = ta.trend.MACD(data['Close'])
    data['MACD'] = macd.macd()
    data['MACD_Signal'] = macd.macd_signal()
    data['MACD_Hist'] = macd.macd_diff()
    bb = ta.volatility.BollingerBands(data['Close'], window=20, window_dev=2)
    data['Upper_BB'] = bb.bollinger_hband()
    data['Lower_BB'] = bb.bollinger_lband()
    data['Volatility'] = data['Close'].pct_change().rolling(window=21).std() * 100
    beta = ticker.info.get('beta', None)

    # Get the latest values
    return {
        'RSI': data['RSI'].iloc[-1],
        'MACD': data['MACD'].iloc[-1],
        'MACD_Signal': data['MACD_Signal'].iloc[-1],
        'MACD_Hist': data['MACD_Hist'].iloc[-1],
        'Upper_BB': data['Upper_BB'].iloc[-1],
        'Lower_BB': data['Lower_BB'].iloc[-1],
        'Volatility': data['Volatility'].iloc[-1],
        'Beta': beta
    }

# Function to score stocks
def score_stock(indicators):
    score = 0
    if indicators['RSI'] < 30:
        score += 1  # Good
    elif 30 <= indicators['RSI'] <= 70:
        score += 0  # Neutral
    else:
        score -= 1  # Bad
    
    if indicators['MACD'] > indicators['MACD_Signal']:
        score += 1  # Bullish signal
    return score

# Function to generate trade recommendations
def generate_recommendations(indicators_list):
    recommendations = {
        'Short Term': [],
        'Medium Term': [],
        'Long Term': []
    }
    
    for stock, indicators in indicators_list.items():
        score = score_stock(indicators)
        current_price = yf.Ticker(stock).history(period="1d")['Close'][-1]
        
        if score > 0:
            stop_loss = current_price * (1 - 0.03)  # Max 3%
            target = current_price * (1 + 0.05)  # Min 5%
            recommendations['Short Term'].append({'Stock': stock, 'Stop Loss': stop_loss, 'Target': target})
        
        if score > 0:
            medium_stop_loss = current_price * (1 - 0.04)  # Max 4%
            medium_target = current_price * (1 + 0.10)  # Min 10%
            recommendations['Medium Term'].append({'Stock': stock, 'Stop Loss': medium_stop_loss, 'Target': medium_target})
        
        if score > 0:
            long_stop_loss = current_price * (1 - 0.05)  # Max 5%
            long_target = current_price * (1 + 0.15)  # Min 15%
            recommendations['Long Term'].append({'Stock': stock, 'Stop Loss': long_stop_loss, 'Target': long_target})

    return recommendations

# Streamlit app
st.title("Stock Analysis and Trading Recommendations")

uploaded_file = st.file_uploader("Upload stocks.xlsx", type=["xlsx"])
if uploaded_file:
    stocks_df = pd.read_excel(uploaded_file)
    stocks = stocks_df['stocks'].tolist()

    # Fetch indicators for each stock
    indicators_list = {stock: fetch_indicators(stock) for stock in stocks}

    # Generate recommendations
    recommendations = generate_recommendations(indicators_list)

    # Display recommendations
    st.subheader("Short Term Trades")
    short_term_df = pd.DataFrame(recommendations['Short Term'])
    st.table(short_term_df.head(20))

    st.subheader("Medium Term Trades")
    medium_term_df = pd.DataFrame(recommendations['Medium Term'])
    st.table(medium_term_df.head(20))

    st.subheader("Long Term Trades")
    long_term_df = pd.DataFrame(recommendations['Long Term'])
    st.table(long_term_df.head(20))
