import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import os
import sys

# ✅ Add parent directory to sys.path so we can import engine
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
sys.path.append(PARENT_DIR)

import engine

# === Streamlit setup ===
st.set_page_config(page_title="EUR/USD AI Dashboard", layout="wide")
st.title("📊 EUR/USD Trading Intelligence Dashboard")

try:
    # === Fetch data ===
    df = engine.fetch_eurusd_data()
    st.success("✅ Data fetched successfully")

    # === Generate signals ===
    trend = engine.get_trend_signal(df)
    sentiment = engine.get_sentiment_signal(df)
    final_signal = engine.generate_trade_signal(trend, sentiment)

    # === Risk management: SL/TP ===
    current_price = df["close"].iloc[-1]
    stop_loss = round(current_price * 0.995, 5)  # SL 0.5% below
    take_profit = round(current_price * 1.01, 5)  # TP 1% above

    # === Telegram alert ===
    engine.send_telegram_alert(signal=final_signal, stop_loss=stop_loss, take_profit=take_profit)

    # === Display signals ===
    st.subheader("🔍 Signal Breakdown")
    col1, col2, col3 = st.columns(3)
    col1.metric("📉 Trend", trend)
    col2.metric("🧠 Sentiment", sentiment)
    col3.metric("🚦 Final Signal", final_signal)

    # === Display chart ===
    st.subheader("📈 EUR/USD Price (Last 5 Days)")
    df_filtered = df[df["datetime"] > pd.Timestamp.now() - pd.Timedelta(days=5)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_filtered["datetime"], y=df_filtered["close"], mode="lines+markers"))
    fig.update_layout(xaxis_title="Date", yaxis_title="Price", height=400)
    st.plotly_chart(fig, use_container_width=True)

    # === Show SL/TP ===
    st.subheader("🎯 SL/TP Levels")
    st.metric("Stop Loss", stop_loss)
    st.metric("Take Profit", take_profit)

except Exception as e:
    st.error(f"❌ Error loading dashboard: {str(e)}")
