import streamlit as st  # First import
st.set_page_config(page_title="EUR/USD AI Dashboard", layout="wide")

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
from alerts.send_telegram_alert import send_telegram_alert

# Load environment variables
load_dotenv()

# App Title
st.title("\U0001F4CA EUR/USD Trading Intelligence Dashboard")

# Sidebar Config Panel
st.sidebar.header("\u2699\ufe0f Configuration")
sl_multiplier = st.sidebar.slider("SL Multiplier", 0.97, 0.999, 0.99)
tp_multiplier = st.sidebar.slider("TP Multiplier", 1.001, 1.05, 1.02)
manual_override = st.sidebar.selectbox("Override Final Signal", ["None", "BUY", "SELL", "NEUTRAL"])

# Fetch Data
df = fetch_eurusd_data()
price = df.iloc[-1]['close']
trend_signal = get_trend_signal(df)
sentiment_signal = get_sentiment_signal(df)
final_signal = generate_trade_signal(trend_signal, sentiment_signal, manual_override)

# Calculate SL/TP
sl, tp = calculate_sl_tp_price(price, final_signal, sl_multiplier, tp_multiplier)

# Log the signal
log_signal(datetime.now(), final_signal, sl, tp)

# Send Telegram Alert
alert_msg = f"""
\U0001F4C8 *New EUR/USD Signal*
*Signal:* {final_signal}
*Price:* {price}
*SL:* {sl}
*TP:* {tp}
"""
send_telegram_alert(alert_msg)

# Display Output
st.subheader("\U0001F50D Signal Breakdown")
col1, col2, col3 = st.columns(3)
col1.metric("\U0001F4CB Trend", trend_signal)
col2.metric("\U0001F9E0 Sentiment", sentiment_signal)
col3.metric("\U0001F7E2 Final Signal", final_signal)

# Plot Price
st.subheader("\U0001F4C8 EUR/USD Price (Last 5 Days)")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['datetime'], y=df['close'], mode='lines+markers'))
fig.update_layout(xaxis_title="Date", yaxis_title="Price")
st.plotly_chart(fig)

# Display SL/TP
st.subheader("\U0001F3AF SL/TP Levels")
st.write("**Stop Loss**")
st.write(sl)
st.write("**Take Profit**")
st.write(tp)