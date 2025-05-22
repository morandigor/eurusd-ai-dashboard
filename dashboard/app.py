import os
import sys
import streamlit as st
import plotly.graph_objects as go

# Add project root to sys.path so imports work
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# ✅ now we can import from signals.engine
from signals.engine import (
    generate_trade_signal,
    get_trend_signal,
    get_smart_money_signal,
    get_sentiment_signal,
)

# UI setup
st.set_page_config(page_title="EUR/USD Dashboard", layout="wide")
st.title("📊 EUR/USD Trading Intelligence Dashboard")

# Generate data
trend = get_trend_signal()
smart_money = get_smart_money_signal()
sentiment = get_sentiment_signal()
final_signal = generate_trade_signal(trend, smart_money, sentiment)

# Display results
st.subheader("🧠 Analysis Overview")
col1, col2, col3 = st.columns(3)
col1.metric("📉 Trend", trend)
col2.metric("💰 Smart Money", smart_money)
col3.metric("💬 Sentiment", sentiment)

st.subheader("🚦 Final Signal")
st.success(f"Suggested Action: {final_signal}")

st.markdown("---")
st.markdown("📈 *(Price chart and SL/TP coming soon...)*")

# Optional placeholder chart
fig = go.Figure()
fig.update_layout(title="EUR/USD Price Chart", height=300, template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)
