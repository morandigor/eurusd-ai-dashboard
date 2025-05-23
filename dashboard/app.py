import streamlit as st
st.set_page_config(page_title="EUR/USD AI Dashboard", layout="wide")

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from dashboard.engine import (
    fetch_eurusd_data,
    get_trend_signal,
    get_sentiment_signal,
    generate_trade_signal,
    log_signal
)


# Sidebar Config Panel
st.sidebar.header("⚙️ Configuration")
sl_multiplier = st.sidebar.slider("SL Multiplier", 0.97, 0.999, 0.99)
tp_multiplier = st.sidebar.slider("TP Multiplier", 1.001, 1.05, 1.02)
manual_override = st.sidebar.selectbox("Override Final Signal", ["None", "BUY", "SELL", "NEUTRAL"])


# Page Setup
st.set_page_config(page_title="EUR/USD AI Dashboard", layout="wide")
st.title("📊 EUR/USD Trading Intelligence Dashboard")

# Fetch Data
data = fetch_eurusd_data()

if data is not None:
    st.success("✅ Data fetched successfully")

    trend_signal = get_trend_signal(data)
    sentiment_signal = get_sentiment_signal(data)

    if manual_override != "None":
        final_signal = manual_override
    else:
        final_signal = generate_trade_signal(trend_signal, sentiment_signal)

    # Display Signals
    st.subheader("🔍 Signal Breakdown")
    cols = st.columns(3)
    cols[0].markdown("🧭 **Trend**")
    cols[0].markdown(f"**{trend_signal}**")
    cols[1].markdown("🧠 **Sentiment**")
    cols[1].markdown(f"**{sentiment_signal}**")
    cols[2].markdown("🟢 **Final Signal**")
    cols[2].markdown(f"**{final_signal}**")

    # Chart
    st.subheader("📉 EUR/USD Price (Last 5 Days)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data["close"], mode="lines", name="EUR/USD"))
    fig.update_layout(xaxis_title="Date", yaxis_title="Price", template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    # SL/TP
    st.subheader("🎯 SL/TP Levels")
    if final_signal in ["BUY", "SELL"]:
        price = float(data["close"].iloc[-1])
        stop_loss, take_profit = calculate_sl_tp(price, final_signal, sl_multiplier, tp_multiplier)
        st.metric("Stop Loss", stop_loss)
        st.metric("Take Profit", take_profit)

        # Log
        timestamp = pd.Timestamp.utcnow()
        log_signal(timestamp, final_signal, stop_loss, take_profit)
    else:
        st.write("No SL/TP generated for NEUTRAL signal.")
