import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import talib as ta  # Install TA-Lib for technical indicators

# Function to fetch stock indicators
def fetch_indicators(stock):
    ticker = yf.Ticker(stock)
    data = ticker.history(period="1y")

    # Calculate indicators
    rsi = ta.RSI(data['Close'], timeperiod=14)[-1] if not data['Close'].isnull().all() else None
    macd, macd_signal, macd_hist = ta.MACD(data['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    upper_bb, middle_bb, lower_bb = ta.BBANDS(data['Close'], timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
    volatility = data['Close'].pct_change().rolling(window=21).std().iloc[-1] * 100 if not data['Close'].isnull().all() else None
    beta = ticker.info['beta']

    return {
        'RSI': rsi,
        'MACD': macd[-1] if macd is not None else None,
        'MACD_Signal': macd_signal[-1] if macd_signal is not None else None,
        'MACD_Hist': macd_hist[-1] if macd_hist is not None else None,
        'Upper_BB': upper_bb[-1] if upper_bb is not None else None,
        'Lower_BB': lower_bb[-1] if lower_bb is not None else None,
        'Volatility': volatility,
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
    
    # Add more scoring logic based on other indicators
    if indicators['MACD'] > indicators['MACD_Signal']:
        score += 1  # Bullish signal
    if indicators['Upper_BB'] < indicators['Close'][-1]:
        score += 1  # Price above Upper BB
    
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
        
        # Repeat similar logic for Medium and Long Term
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
