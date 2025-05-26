# app.py

# ✅ Streamlit config must be FIRST
import streamlit as st
st.set_page_config(page_title="EUR/USD AI Dashboard", layout="wide")

# ✅ Other imports
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from dotenv import load_dotenv
import os

# ✅ App-specific logic
from app.engine import (
    fetch_eurusd_data,
    get_trend_signal,
    get_sentiment_signal,
    generate_trade_signal,
    calculate_sl_tp_price,
    log_signal,
)

# ✅ Telegram alert (update path based on your folder structure)
from alerts.telegram import send_telegram_alert

# ✅ Load environment variables (.env)
load_dotenv()

# === App UI ===
st.title("📊 EUR/USD Trading Intelligence Dashboard")

# Sidebar
st.sidebar.header("⚙️ Configuration")
sl_multiplier = st.sidebar.slider("SL Multiplier", 0.97, 1.0, 0.97)
tp_multiplier = st.sidebar.slider("TP Multiplier", 1.0, 1.05, 1.00)
manual_override = st.sidebar.selectbox("Override Final Signal", ["None", "BUY", "SELL", "NEUTRAL"])

# === Data + Signal Logic ===
df = fetch_eurusd_data()

# Make sure 'close' exists
if 'close' not in df.columns:
    st.error("❌ Data error: 'close' column not found in DataFrame.")
    st.dataframe(df)
else:
    price = df['close'].iloc[-1]
    trend_signal = get_trend_signal(df)
    sentiment_signal = get_sentiment_signal(df)
    final_signal = generate_trade_signal(trend_signal, sentiment_signal)

    if manual_override != "None":
        final_signal = manual_override

    sl, tp = calculate_sl_tp_price(price, final_signal, sl_multiplier, tp_multiplier)
    log_signal(datetime.now(), final_signal, sl, tp)

    # === Alerts ===
    send_telegram_alert(f"📈 EUR/USD Signal: {final_signal}\nSL: {sl}\nTP: {tp}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # === Dashboard ===
    st.subheader("🔍 Signal Breakdown")
    col1, col2, col3 = st.columns(3)
    col1.metric("📉 Trend", trend_signal)
    col2.metric("📊 Sentiment", sentiment_signal)
    col3.metric("✅ Final Signal", final_signal)

    # === Chart ===
    st.subheader("📉 EUR/USD Price (Last 5 Days)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['datetime'], y=df['close'], mode='lines+markers', name='Close'))
    st.plotly_chart(fig, use_container_width=True)

    # === SL/TP ===
    st.subheader("🎯 SL/TP Levels")
    st.markdown(f"**Stop Loss:** `{sl}`")
    st.markdown(f"**Take Profit:** `{tp}`")
