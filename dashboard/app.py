import streamlit as st
import os
import sys
import plotly.graph_objects as go

# Add project root to the path so we can import from signals.engine
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.append(PROJECT_ROOT)

from signals.engine import (
    generate_trade_signal,
    get_trend_signal,
    get_sentiment_signal
)

st.set_page_config(page_title="EUR/USD Trading Intelligence", layout="wide")
st.title("📊 EUR/USD Trading Intelligence Dashboard")

# === Fetch signals ===
trend = get_trend_signal()
sentiment = get_sentiment_signal()

# === Generate final signal ===
final_signal = generate_trade_signal(trend, sentiment)

# === Display output ===
st.subheader("📈 Final Trading Signal")
st.success(f"The model recommends: **{final_signal}**")

# === Optional Chart ===
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
    y=[1.08, 1.10, 1.09, 1.11, 1.12],
    mode="lines+markers",
    name="EUR/USD Example"
))
fig.update_layout(title="EUR/USD Sample Price Trend")
st.plotly_chart(fig)
