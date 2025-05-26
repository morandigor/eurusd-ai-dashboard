import streamlit as st
st.set_page_config(page_title="EUR/USD AI Dashboard", layout="wide")  # ✅ Must be first

# ✅ All safe imports after that
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import os
from dotenv import load_dotenv

# ✅ Load environment
load_dotenv()

# ✅ Now import internal modules
from app.engine import (
    fetch_eurusd_data,
    get_trend_signal,
    get_sentiment_signal,
    generate_trade_signal,
    calculate_sl_tp_price,
    log_signal,
)

from app.telegram import send_telegram_alert


# ✅ Load data
df = fetch_eurusd_data()
price = df["price"].iloc[-1]

# ✅ Signal logic
trend = get_trend_signal(df)
sentiment = get_sentiment_signal(df)
final_signal = generate_trade_signal(trend, sentiment)

# ✅ Sidebar
sl_multiplier = st.sidebar.slider("SL Multiplier", 0.97, 1.00, 0.99)
tp_multiplier = st.sidebar.slider("TP Multiplier", 1.00, 1.05, 1.01)

# ✅ SL/TP calc
sl, tp = calculate_sl_tp_price(price, final_signal, sl_multiplier, tp_multiplier)

# ✅ Log + Alert
log_signal(datetime.now(), final_signal, sl, tp)
send_telegram_alert(f"Signal: {final_signal}, SL: {sl:.4f}, TP: {tp:.4f}")

# ✅ Streamlit UI
st.title("📈 EUR/USD Trading Intelligence Dashboard")
st.subheader("Latest Signal: " + final_signal)
st.plotly_chart(go.Figure(data=[go.Scatter(x=df["timestamp"], y=df["price"])]))