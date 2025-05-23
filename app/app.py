# app.py

import streamlit as st  # ✅ Must be the first import
st.set_page_config(page_title="EUR/USD AI Dashboard", layout="wide")  # ✅ Must be first Streamlit command

# Other imports
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Import engine functions
from engine import (
    fetch_eurusd_data,
    get_trend_signal,
    get_sentiment_signal,
    generate_trade_signal,
    calculate_sl_tp_price,
    log_signal
)

# Title
st.title("📊 EUR/USD Trading Intelligence Dashboard")

# Sidebar configuration
st.sidebar.header("⚙️ Configuration")
sl_multiplier = st.sidebar.slider("SL Multiplier", 0.97, 0.999, 0.99)
tp_multiplier = st.sidebar.slider("TP Multiplier", 1.001, 1.05, 1.02)
manual_override = st.sidebar.selectbox("Override Final Signal", ["None", "BUY", "SELL", "NEUTRAL"])

# Fetch and prepare data
df = fetch_eurusd_data()
trend = get_trend_signal(df)
sentiment = get_sentiment_signal()
final_signal = generate_trade_signal(trend, sentiment, manual_override)

# Calculate SL/TP
price = df['close'].iloc[-1]
sl, tp = calculate_sl_tp_price(price, final_signal, sl_multiplier, tp_multiplier)

# Log signal
log_signal(datetime.now(), final_signal, sl, tp)

# Display signals and chart
st.subheader("🔍 Signal Breakdown")
col1, col2, col3 = st.columns(3)
col1.metric("📉 Trend", trend)
col2.metric("🧠 Sentiment", sentiment)
col3.metric("🟢 Final Signal", final_signal)

st.subheader("📉 EUR/USD Price (Last 5 Days)")
fig = go.Figure(data=[go.Scatter(x=df['datetime'], y=df['close'], mode='lines+markers')])
fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig, use_container_width=True)

st.subheader("🎯 SL/TP Levels")
col1, col2 = st.columns(2)
col1.metric("Stop Loss", round(sl, 5))
col2.metric("Take Profit", round(tp, 5))
