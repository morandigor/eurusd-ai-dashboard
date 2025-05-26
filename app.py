import streamlit as st

# Deve ser o primeiro comando do Streamlit
st.set_page_config(page_title="EUR/USD AI Dashboard", layout="wide")

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from dotenv import load_dotenv
import os

# ⚙️ Load .env
load_dotenv()

# 📦 Imports do projeto
from app.engine import (
    fetch_eurusd_data,
    get_trend_signal,
    get_sentiment_signal,
    generate_trade_signal,
    calculate_sl_tp_price,
    log_signal,
)
from app.telegram import send_telegram_alert

# ============================
# 🧠 DASHBOARD LÓGICA
# ============================

st.title("📈 EUR/USD AI Trading Dashboard")

# 🔍 Dados
data = fetch_eurusd_data()
trend_signal = get_trend_signal(data)
sentiment_signal = get_sentiment_signal()
trade_signal = generate_trade_signal(trend_signal, sentiment_signal)
sl, tp = calculate_sl_tp_price(data)
log_signal(trade_signal, sl, tp)

# 🧾 Exibição
st.subheader("📊 Signal Generated")
st.markdown(f"**Trade Signal:** `{trade_signal}`")
st.markdown(f"**Stop Loss:** `{sl}` | **Take Profit:** `{tp}`")
st.markdown(f"**Trend Signal:** `{trend_signal}`")
st.markdown(f"**Sentiment Signal:** `{sentiment_signal}`")

# 📈 Gráfico
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=data['time'],
    open=data['open'],
    high=data['high'],
    low=data['low'],
    close=data['close'],
    name="EUR/USD"
))
st.plotly_chart(fig, use_container_width=True)

# 🚀 Alerta Telegram
if trade_signal in ["BUY", "SELL"]:
    send_telegram_alert(trade_signal, sl, tp)
    st.success("📬 Alerta enviado automaticamente!")
else:
    st.info("⚪ Nenhum alerta enviado. Sinal atual: WAIT.")

