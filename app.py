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
# ============================
# 📊 PAINEL DE PERFORMANCE
# ============================

st.markdown("---")
st.header("📈 Histórico de Sinais")

import os

if os.path.exists("signals_log.csv"):
    df_log = pd.read_csv("signals_log.csv")
    df_log["Timestamp"] = pd.to_datetime(df_log["Timestamp"])

    # 📌 Filtro por tipo de sinal
    filtro = st.selectbox("📌 Filtrar por tipo de sinal:", options=["Todos", "BUY", "SELL", "WAIT"])
    if filtro != "Todos":
        df_log = df_log[df_log["Signal"] == filtro]

    # 📉 Mostrar últimos 20 sinais
    st.subheader("🧾 Últimos 20 sinais")
    st.dataframe(df_log.sort_values("Timestamp", ascending=False).head(20), use_container_width=True)

    # 📊 Estatísticas rápidas
    st.subheader("📊 Estatísticas")
    total = len(df_log)
    enviados = len(df_log[df_log["Sent"] == "Yes"])
    por_envio = round(enviados / total * 100, 2) if total else 0

    buy_count = len(df_log[df_log["Signal"] == "BUY"])
    sell_count = len(df_log[df_log["Signal"] == "SELL"])
    wait_count = len(df_log[df_log["Signal"] == "WAIT"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Sinais", total)
    col2.metric("Alertas Enviados", enviados)
    col3.metric("Taxa de Envio (%)", por_envio)
    col4.metric("Sinais BUY / SELL / WAIT", f"{buy_count} / {sell_count} / {wait_count}")
else:
    st.warning("Nenhum log de sinal encontrado ainda.")
