import streamlit as st
import sqlite3
import pandas as pd
from signals.engine import generate_trade_signal, get_trend_signal, get_cot_bias, get_sentiment_signal
import time

st.set_page_config(page_title="EUR/USD Dashboard", layout="wide")

# Auto-refresh every 60 seconds
st.experimental_set_query_params(_=int(time.time()))
st.markdown("<meta http-equiv='refresh' content='60'>", unsafe_allow_html=True)

st.title("💹 EUR/USD Intelligence Dashboard")

# Signal overview
st.subheader("📊 Current Market Signals")
col1, col2, col3 = st.columns(3)
col1.metric("Trend Signal", get_trend_signal())
col2.metric("Smart Money", get_cot_bias())
col3.metric("Sentiment", get_sentiment_signal())

# Final signal
signal_data = generate_trade_signal()

if isinstance(signal_data, dict):
    st.markdown(f"### 🚨 Trade Signal: **{signal_data['signal']}**")
else:
    st.markdown(f"### 🚨 Trade Signal: **{signal_data}**")

# Price chart with SL/TP
st.subheader("📈 EUR/USD Price Chart")
conn = sqlite3.connect("db/database.db")
prices = pd.read_sql("SELECT * FROM eurusd_prices ORDER BY timestamp DESC LIMIT 100", conn)
conn.close()
prices = prices.sort_values("timestamp")
st.line_chart(prices.set_index("timestamp")["close"])

# SL/TP overlay chart
if isinstance(signal_data, dict):
    entry = signal_data["entry"]
    tp = signal_data["tp"]
    sl = signal_data["sl"]
    overlay_df = pd.DataFrame({
        "Entry": [entry] * len(prices),
        "TP": [tp] * len(prices),
        "SL": [sl] * len(prices)
    }, index=prices["timestamp"])
    st.line_chart(overlay_df)

# Economic events table
st.subheader("📅 Economic Events")
conn = sqlite3.connect("db/database.db")
events = pd.read_sql("SELECT * FROM economic_events ORDER BY timestamp DESC LIMIT 10", conn)
conn.close()
st.table(events)

st.markdown("---")
st.caption("Built with 💼 by MrDin's EUR/USD AI Engine")