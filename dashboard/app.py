import streamlit as st
import plotly.graph_objects as go
import os
import sys

# === Ensure local imports work ===
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.append(PROJECT_ROOT)

from signals.engine import (
    fetch_price_data,
    get_trend_signal,
    get_sentiment_signal,
    generate_trade_signal,
    send_alert,
)

# === Streamlit UI Setup ===
st.set_page_config(page_title="EUR/USD TradeIntel AI", layout="wide")
st.title("📊 EUR/USD Trading Intelligence Dashboard")

# === Fetch and process data ===
try:
    df = fetch_price_data()
    st.success("✅ Data fetched successfully")

    trend = get_trend_signal(df)
    sentiment = get_sentiment_signal()
    signal = generate_trade_signal(trend, sentiment)

    # === Display signals ===
    st.subheader("🔍 Signal Breakdown")
    col1, col2, col3 = st.columns(3)
    col1.metric("📈 Trend", trend)
    col2.metric("🧠 Sentiment", sentiment)
    col3.metric("🚦 Final Signal", signal)

    # === Chart ===
    st.subheader("📉 EUR/USD Close Price (Last 5 Days)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["datetime"],
        y=df["close"],
        mode="lines+markers",
        name="EUR/USD"
    ))
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # === Telegram Alert ===
    send_alert(f"🚨 TradeIntel Signal: {signal} | Trend: {trend}, Sentiment: {sentiment}")

except Exception as e:
    st.error(f"❌ Failed to load dashboard: {str(e)}")
