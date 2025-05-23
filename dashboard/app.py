import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from engine import generate_trade_signal, log_signal
import datetime
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TWELVE_DATA_API_KEY")

st.set_page_config(page_title="EUR/USD Trading Intelligence Dashboard", layout="wide")
st.title("\U0001F4CA EUR/USD Trading Intelligence Dashboard")

@st.cache_data
def fetch_eurusd_data():
    url = f"https://api.twelvedata.com/time_series?symbol=EUR/USD&interval=1h&apikey={API_KEY}&outputsize=120"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data['values'])
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values("datetime")
    df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
    return df

df = fetch_eurusd_data()

# Signal Generation
signal, sl, tp = generate_trade_signal(df)
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
log_signal(timestamp, signal, sl, tp)

# Display Dashboard
st.success("\u2705 Data fetched successfully")

st.subheader("\U0001F50D Signal Breakdown")
st.markdown(f"**\U0001F4CB Trend**\n{get_trend_signal(df)}")
st.markdown(f"**\U0001F9E0 Sentiment**\n{get_sentiment_signal(df)}")
st.markdown(f"**\U0001F4E1 Final Signal**\n{signal}")

st.subheader("\U0001F4C8 EUR/USD Price (Last 5 Days)")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['datetime'], y=df['close'], mode='lines+markers', name='Close'))
fig.update_layout(xaxis_title='Date', yaxis_title='Price')
st.plotly_chart(fig, use_container_width=True)

st.subheader("\U0001F3AF SL/TP Levels")
st.metric("Stop Loss", sl)
st.metric("Take Profit", tp)