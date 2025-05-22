import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import sys
import os

# Add parent directory to sys.path so Streamlit Cloud can find 'signals'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from signals.engine import (
    generate_trade_signal,
    get_trend_signal,
    get_smart_money_signal,
    get_sentiment_signal,
)

# Streamlit App
st.set_page_config(layout="wide", page_title="EUR/USD Trading Intelligence")

st.title("📈 EUR/USD Trading Intelligence")

# Load and display signals
trend = get_trend_signal()
smart_money = get_smart_money_signal()
sentiment = get_sentiment_signal()
trade_signal = generate_trade_signal(trend, smart_money, sentiment)

# Display current signals
st.subheader("📊 Current Market Signals")
col1, col2, col3 = st.columns(3)
col1.metric("Trend Signal", trend)
col2.metric("Smart Money", smart_money)
col3.metric("Sentiment", sentiment)

# Trade signal
st.subheader("🚨 Trade Signal")
st.markdown(f"### {trade_signal}")

# Sample dummy chart
st.subheader("📉 EUR/USD Price Chart")
df = pd.DataFrame({
    "time": pd.date_range(end=pd.Timestamp.now(), periods=20, freq="H"),
    "price": [1.08 + 0.002 * i for i in range(20)]
})
fig = go.Figure(data=[go.Scatter(x=df["time"], y=df["price"], mode="lines", name="EUR/USD")])
fig.update_layout(margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig, use_container_width=True)
