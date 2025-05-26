import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# 📦 Importa lógica personalizada
from app.engine import (
    fetch_eurusd_data,
    get_trend_signal,
    get_sentiment_signal,
    calculate_sl_tp,
    generate_trade_signal,
    log_to_supabase
)

from app.telegram import send_telegram_alert

# 🛠️ Configura a página
st.set_page_config(page_title="EUR/USD AI Trading Dashboard", layout="wide")

# 🚀 Coleta dados
data = fetch_eurusd_data()

# 🧠 Sinais
trend_signal = get_trend_signal(data)
sentiment_signal = get_sentiment_signal(data)
trade_signal = generate_trade_signal(data, trend_signal, sentiment_signal)

# 🎯 Preço atual
current_price = data["close"].iloc[-1]

# 🛡️ SL e TP
sl, tp = calculate_sl_tp(data, trade_signal)

# 📤 Envia alerta se for BUY ou SELL
if trade_signal in ["BUY", "SELL"]:
    msg = f"""
📊 EUR/USD Signal Generated!

📈 Trade Signal: {trade_signal}
🔻 Stop Loss: {sl:.5f}
🎯 Take Profit: {tp:.5f}
📉 Trend Signal: {trend_signal}
🧠 Sentiment Signal: {sentiment_signal}
💰 Entry Price: {current_price:.5f}
🕒 Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
"""
    send_telegram_alert(msg)

# 🧾 Loga no Supabase
log_to_supabase(
    signal=trade_signal,
    sl=sl,
    tp=tp,
    trend=trend_signal,
    sentiment=sentiment_signal,
    price=current_price,
)

# 🖼️ Título e Sinal
st.title("📉 EUR/USD AI Trading Dashboard")
st.subheader("📊 Sinal Gerado")
st.markdown(f"**Trade Signal:** `{trade_signal}`")
st.markdown(f"**Stop Loss:** `{sl:.5f}` | **Take Profit:** `{tp:.5f}`")
st.markdown(f"**Trend Signal:** `{trend_signal}`")
st.markdown(f"**Sentiment Signal:** `{sentiment_signal}`")

# 📈 Gráfico
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=data.index,
    open=data["open"],
    high=data["high"],
    low=data["low"],
    close=data["close"],
    name="EUR/USD"
))
fig.update_layout(height=400, margin=dict(l=0, r=0, t=0, b=0))
st.plotly_chart(fig, use_container_width=True)
