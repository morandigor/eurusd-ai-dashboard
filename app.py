import streamlit as st

st.set_page_config(page_title="EUR/USD AI Dashboard", layout="wide")

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

from app.engine import (
    fetch_eurusd_data,
    get_trend_signal,
    get_sentiment_signal,
    generate_trade_signal,
    calculate_sl_tp_price,
    log_signal,
    log_to_csv,
)
from app.telegram import send_telegram_alert

# ============================
# 📊 DASHBOARD
# ============================

st.title("📈 EUR/USD AI Trading Dashboard")

# 🔍 Dados e sinais
data = fetch_eurusd_data()
trend_signal = get_trend_signal(data)
sentiment_signal = get_sentiment_signal()
trade_signal = generate_trade_signal(trend_signal, sentiment_signal)
sl, tp = calculate_sl_tp_price(data)
log_signal(trade_signal, sl, tp)

current_price = data["close"].iloc[-1]
was_sent = trade_signal in ["BUY", "SELL"]
log_to_csv(trade_signal, sl, tp, trend_signal, sentiment_signal, current_price, was_sent)

# 🧾 Exibição
st.subheader("📊 Sinal Gerado")
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

# ============================
# 📩 ALERTA AUTOMÁTICO TELEGRAM
# ============================

if was_sent:
    send_telegram_alert(trade_signal, sl, tp)
    st.success(f"📬 Alerta enviado automaticamente para: {trade_signal}")
else:
    st.info("⚪ Nenhum alerta enviado. Sinal atual: WAIT.")

# ============================
# 🔄 AUTO-REFRESH A CADA 15 MIN
# ============================

if "last_refresh" not in st.session_state:
    st.session_state["last_refresh"] = time.time()

elapsed = time.time() - st.session_state["last_refresh"]

if elapsed > 900:
    st.session_state["last_refresh"] = time.time()
    st.experimental_rerun()
else:
    remaining = 900 - int(elapsed)
    mins, secs = divmod(remaining, 60)
    st.sidebar.info(f"⏳ Atualização automática em {mins:02d}:{secs:02d}")
