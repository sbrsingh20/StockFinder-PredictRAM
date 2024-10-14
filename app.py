import streamlit as st
import pandas as pd
import yfinance as yf
import ta

# Function to fetch stock indicators
def fetch_indicators(stock):
    ticker = yf.Ticker(stock)
    data = ticker.history(period="1y")

    if data.empty:
        return {
            'RSI': None,
            'MACD': None,
            'MACD_Signal': None,
            'MACD_Hist': None,
            'Upper_BB': None,
            'Lower_BB': None,
            'Volatility': None,
            'Beta': None,
            'Close': None
        }

    # Calculate indicators
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

    try:
        return {
            'RSI': data['RSI'].iloc[-1],
            'MACD': data['MACD'].iloc[-1],
            'MACD_Signal': data['MACD_Signal'].iloc[-1],
            'MACD_Hist': data['MACD_Hist'].iloc[-1],
            'Upper_BB': data['Upper_BB'].iloc[-1],
            'Lower_BB': data['Lower_BB'].iloc[-1],
            'Volatility': data['Volatility'].iloc[-1],
            'Beta': beta,
            'Close': data['Close'].iloc[-1]
        }
    except IndexError:
        return {
            'RSI': None,
            'MACD': None,
            'MACD_Signal': None,
            'MACD_Hist': None,
            'Upper_BB': None,
            'Lower_BB': None,
            'Volatility': None,
            'Beta': None,
            'Close': None
        }

# Function to score stocks based on indicators
def score_stock(indicators):
    score = 0

    # RSI scoring
    if indicators['RSI'] is not None:
        if 30 <= indicators['RSI'] <= 70:
            score += 1  # Good
        if 40 <= indicators['RSI'] <= 60:
            score += 0  # Neutral
        if indicators['RSI'] < 30 or indicators['RSI'] > 70:
            score -= 1  # Bad

    # MACD scoring
    if indicators['MACD'] is not None and indicators['MACD_Signal'] is not None:
        if indicators['MACD'] > indicators['MACD_Signal']:
            score += 1  # Good
        elif indicators['MACD'] < 0:
            score -= 1  # Bad

    # MACD Signal scoring
    if indicators['MACD_Signal'] is not None:
        if indicators['MACD_Signal'] > 0:
            score += 1  # Good
        elif indicators['MACD_Signal'] < 0:
            score -= 1  # Bad

    # MACD Histogram scoring
    if indicators['MACD_Hist'] is not None:
        if indicators['MACD_Hist'] > 0:
            score += 1  # Good
        elif indicators['MACD_Hist'] < 0:
            score -= 1  # Bad

    # Bollinger Bands scoring
    if indicators['Upper_BB'] is not None and indicators['Lower_BB'] is not None:
        if indicators['Close'] >= indicators['Upper_BB']:
            score += 1  # Good (bullish signal)
        elif indicators['Close'] <= indicators['Lower_BB']:
            score -= 1  # Bad (bearish signal)

    # Volatility scoring
    if indicators['Volatility'] is not None:
        if 10 <= indicators['Volatility'] <= 20:  # Adjust range as needed
            score += 1  # Good
        elif indicators['Volatility'] < 10 or indicators['Volatility'] > 20:
            score -= 1  # Bad

    # Beta scoring
    if indicators['Beta'] is not None:
        if 0.8 <= indicators['Beta'] <= 1.2:
            score += 1  # Good
        elif indicators['Beta'] < 0.8 or indicators['Beta'] > 1.2:
            score -= 1  # Bad

    return score

# Function to generate recommendations
def generate_recommendations(indicators_list):
    recommendations = {
        'Short Term': [],
        'Medium Term': [],
        'Long Term': []
    }
    
    for stock, indicators in indicators_list.items():
        score = score_stock(indicators)
        current_price = indicators['Close']
        
        if current_price is not None:
            lower_buy_range = current_price * 0.995  # 0.5% lower
            upper_buy_range = current_price * 1.005  # 0.5% higher
            short_stop_loss = current_price * (1 - 0.03)  # Max 3%
            short_target = current_price * (1 + 0.05)  # Min 5%
            medium_stop_loss = current_price * (1 - 0.04)  # Max 4%
            medium_target = current_price * (1 + 0.10)  # Min 10%
            long_stop_loss = current_price * (1 - 0.05)  # Max 5%
            long_target = current_price * (1 + 0.15)  # Min 15%

            recommendations['Short Term'].append({
                'Stock': stock,
                'Current Price': current_price,
                'Lower Buy Range': lower_buy_range,
                'Upper Buy Range': upper_buy_range,
                'Stop Loss': short_stop_loss,
                'Target Price': short_target,
                'Score': score
            })
            recommendations['Medium Term'].append({
                'Stock': stock,
                'Current Price': current_price,
                'Lower Buy Range': lower_buy_range,
                'Upper Buy Range': upper_buy_range,
                'Stop Loss': medium_stop_loss,
                'Target Price': medium_target,
                'Score': score
            })
            recommendations['Long Term'].append({
                'Stock': stock,
                'Current Price': current_price,
                'Lower Buy Range': lower_buy_range,
                'Upper Buy Range': upper_buy_range,
                'Stop Loss': long_stop_loss,
                'Target Price': long_target,
                'Score': score
            })

    return recommendations

# Streamlit app
st.title("Stock Analysis and Trading Recommendations")

# Read stock symbols from stocks.xlsx
stocks_df = pd.read_excel('stocks.xlsx')
stocks = stocks_df['stocks'].tolist()

# Fetch indicators for each stock
indicators_list = {stock: fetch_indicators(stock) for stock in stocks}

# Generate recommendations
recommendations = generate_recommendations(indicators_list)

# Display top 20 recommendations for each term
st.subheader("Top 20 Short Term Trades")
short_term_df = pd.DataFrame(recommendations['Short Term']).sort_values(by='Score', ascending=False).head(20)
st.table(short_term_df)

st.subheader("Top 20 Medium Term Trades")
medium_term_df = pd.DataFrame(recommendations['Medium Term']).sort_values(by='Score', ascending=False).head(20)
st.table(medium_term_df)

st.subheader("Top 20 Long Term Trades")
long_term_df = pd.DataFrame(recommendations['Long Term']).sort_values(by='Score', ascending=False).head(20)
st.table(long_term_df)
