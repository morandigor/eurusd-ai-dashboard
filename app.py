import streamlit as st

# ✅ MUST be the first Streamlit command
st.set_page_config(page_title="EUR/USD AI Dashboard", layout="wide")

# 📦 Standard libraries
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv

# 🧠 Engine functions
from app.engine import (
    fetch_eurusd_data,
    get_trend_signal,
    get_sentiment_signal,
    generate_trade_signal,
    calculate_sl_tp_price,
    log_signal,
)

# 📲 Telegram alert
from app.telegram import send_telegram_alert

# 🔧 Load environment variables
load_dotenv()

# =========================================
# 📊 APP LAYOUT
# =========================================

st.title("📈 EUR/USD AI Trading Dashboard")

# 📥 Fetch data
data = fetch_eurusd_data()
trend_signal = get_trend_signal(data)
sentiment_signal = get_sentiment_signal()
trade_signal = generate_trade_signal(trend_signal, sentiment_signal)
sl, tp = calculate_sl_tp_price(data)
log_signal(trade_signal, sl, tp)

# 📤 Show output
st.subheader("Signal Summary")
st.markdown(f"**Trade Signal:** `{trade_signal}`")
st.markdown(f"**Stop Loss:** `{sl}` | **Take Profit:** `{tp}`")
st.markdown(f"**Trend Signal:** `{trend_signal}`")
st.markdown(f"**Sentiment Signal:** `{sentiment_signal}`")

# 📈 Plotting
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=data['time'],
    open=data['open'],
    high=data['high'],
    low=data['low'],
    close=data['close'],
    name="EUR/USD"
))
st.plotly_chart(fig, use_container_width=True)

# 📬 Alert
if st.button("Send Telegram Alert"):
    send_telegram_alert(trade_signal, sl, tp)
    st.success("Telegram alert sent!")