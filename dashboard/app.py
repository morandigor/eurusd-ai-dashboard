import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# 👇 Fix path for imports when deployed on Streamlit Cloud
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 👇 Import signal engine
from signals.engine import generate_trade_signal, get_trend_signal, get_combined_signal

# === PAGE CONFIG ===
st.set_page_config(
    page_title="EUR/USD Trading Intelligence",
    page_icon="📈",
    layout="wide"
)

# === TITLE ===
st.markdown("## 💹 EUR/USD Trading Intelligence")

# === SIGNAL ENGINE ===
try:
    signal_data = generate_trade_signal()
    trend = get_trend_signal()
    confidence = get_confidence_level()
except Exception as e:
    st.error(f"❌ Error fetching signals: {e}")
    st.stop()

# === SIGNAL STATUS ===
st.subheader("📊 Current Market Signals")
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("Trend Signal")
    st.markdown(f"**{trend}**")

with col2:
    st.caption("Smart Money")
    st.markdown(f"**{confidence}**")

with col3:
    st.caption("Sentiment")
    st.markdown(f"**{signal_data.get('sentiment', 'Unknown')}**")

# === TRADE DECISION ===
trade_signal = signal_data.get("signal", "WAIT / NO CLEAR EDGE")
st.markdown(f"### 🔴 Trade Signal: ⏸️ {trade_signal}")

# === CHART ===
st.subheader("📉 EUR/USD Price Chart")

price_data = signal_data.get("price_data", pd.DataFrame())

if not price_data.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=price_data['datetime'], y=price_data['close'], mode='lines', name='EUR/USD'))
    fig.update_layout(
        xaxis_title='Time',
        yaxis_title='Price',
        margin=dict(l=0, r=0, t=10, b=10),
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ No price data available.")

# === AUTO-REFRESH ===
st.experimental_set_query_params()
st.experimental_rerun()
