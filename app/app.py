import streamlit as st  # First import
st.set_page_config(page_title="EUR/USD AI Dashboard", layout="wide")  # Must be second

# Other imports
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from dotenv import load_dotenv
import os

from engine import (
    fetch_eurusd_data,
    get_trend_signal,
    get_sentiment_signal,
    generate_trade_signal,
    calculate_sl_tp_price,
    log_signal,
)
from alerts.telegram import send_telegram_alert


# Load environment variables
load_dotenv()

# App Title
st.title("📊 EUR/USD Trading Intelligence Dashboard")

# Sidebar Config Panel
st.sidebar.header("⚙️ Configuration")
sl_multiplier = st.sidebar.slider("SL Multiplier", 0.97, 0.999, 0.99)
tp_multiplier = st.sidebar.slider("TP Multiplier", 1.001, 1.05, 1.02)
manual_override = st.sidebar.selectbox("Override Final Signal", ["None", "BUY", "SELL", "NEUTRAL"])

# Fetch and display data
df = fetch_eurusd_data()
price = df['price'].iloc[-1]
trend_signal = get_trend_signal(df)
sentiment_signal = get_sentiment_signal(df)
final_signal = generate_trade_signal(trend_signal, sentiment_signal)

# Apply override if any
if manual_override != "None":
    final_signal = manual_override

# Calculate SL/TP
sl, tp = calculate_sl_tp_price(price, final_signal, sl_multiplier, tp_multiplier)

# Log signal
log_signal(datetime.now(), final_signal, sl, tp)

# 🔔 Telegram Alert
if final_signal in ["BUY", "SELL"]:
    alert_msg = f"\n🚨 EUR/USD SIGNAL\nSignal: {final_signal}\nSL: {sl}\nTP: {tp}"
    send_telegram_alert(alert_msg)

# Display
st.subheader("🔍 Signal Breakdown")
col1, col2, col3 = st.columns(3)
col1.markdown("**📉 Trend**")
col1.markdown(f"**{trend_signal}**")
col2.markdown("**🧠 Sentiment**")
col2.markdown(f"**{sentiment_signal}**")
col3.markdown("**🟢 Final Signal**")
col3.markdown(f"**{final_signal}**")

# Chart
st.subheader("📉 EUR/USD Price (Last 5 Days)")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['datetime'], y=df['price'], mode='lines+markers'))
fig.update_layout(xaxis_title='Date', yaxis_title='Price')
st.plotly_chart(fig, use_container_width=True)

# SL/TP Display
st.subheader("🎯 SL/TP Levels")
st.markdown(f"**Stop Loss**\n\n{sl}")
st.markdown(f"**Take Profit**\n\n{tp}")