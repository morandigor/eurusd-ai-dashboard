import streamlit as st

# 🔧 Must be the very first Streamlit call
st.set_page_config(page_title="EUR/USD AI Dashboard", layout="wide")

# 🧠 Other imports
import os
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from dotenv import load_dotenv

# 🧠 App logic imports
from app.engine import (
    fetch_eurusd_data,
    get_trend_signal,
    get_sentiment_signal,
    generate_trade_signal,
    calculate_sl_tp_price,
    log_signal,
)
from alerts.telegram import send_telegram_alert

# ✅ Load environment variables
load_dotenv()

# 📊 App Title
st.title("📊 EUR/USD Trading Intelligence Dashboard")

# 🔧 Sidebar config
st.sidebar.header("⚙️ Configuration")
sl_multiplier = st.sidebar.slider("SL Multiplier", 0.97, 1.00, 0.99)
tp_multiplier = st.sidebar.slider("TP Multiplier", 1.00, 1.05, 1.02)
manual_override = st.sidebar.selectbox("Override Final Signal", ["None", "BUY", "SELL", "NEUTRAL"])

# 📈 Fetch data
df = fetch_eurusd_data()
if df.empty or 'price' not in df.columns:
    st.error("No data or 'price' column missing.")
    st.stop()

price = df["price"].iloc[-1]
trend_signal = get_trend_signal(df)
sentiment_signal = get_sentiment_signal(df)

# ✳️ Final signal logic
final_signal = manual_override if manual_override != "None" else generate_trade_signal(trend_signal, sentiment_signal)
sl, tp = calculate_sl_tp_price(price, final_signal, sl_multiplier, tp_multiplier)

# 📝 Log + Alert
log_signal(datetime.now(), final_signal, sl, tp)
send_telegram_alert(final_signal, sl, tp)

# 📊 Display
st.subheader("🔍 Signal Breakdown")
cols = st.columns(3)
cols[0].metric("📉 Trend", trend_signal)
cols[1].metric("📢 Sentiment", sentiment_signal)
cols[2].metric("✅ Final Signal", final_signal)

st.subheader("📉 EUR/USD Price (Last 5 Days)")
st.line_chart(df.set_index("timestamp")["price"])

st.subheader("🎯 SL/TP Levels")
st.write(f"**Stop Loss**: {sl}")
st.write(f"**Take Profit**: {tp}")
