import streamlit as st

# Configuração da página
st.set_page_config(page_title="EUR/USD AI Dashboard", layout="wide")

import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import os

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
# 🔍 PROCESSAMENTO DE SINAL
# ============================

st.title("📈 EUR/USD AI Trading Dashboard")

# Obter dados e gerar sinal
data = fetch_eurusd_data()
trend_signal = get_trend_signal(data)
sentiment_signal = get_sentiment_signal()
trade_signal = generate_trade_signal(trend_signal, sentiment_signal)
sl, tp = calculate_sl_tp_price(data)
log_signal(trade_signal, sl, tp)

# Coleta de preços atuais e futuros
entry_price = data["close"].iloc[-1]
future_high = data["high"].iloc[-1]    # OU .iloc[-2] se já passou
future_low = data["low"].iloc[-1]
was_sent = trade_signal in ["BUY", "SELL"]

# Log completo com simulação de resultado
log_to_csv(
    trade_signal, sl, tp, trend_signal, sentiment_signal,
    entry_price, was_sent, future_high, future_low
)

# Exibição do sinal
st.subheader("📊 Sinal Gerado")
st.markdown(f"**Trade Signal:** `{trade_signal}`")
st.markdown(f"**Stop Loss:** `{sl}` | **Take Profit:** `{tp}`")
st.markdown(f"**Trend Signal:** `{trend_signal}`")
st.markdown(f"**Sentiment Signal:** `{sentiment_signal}`")

# Gráfico de candle
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
# 📩 ENVIO AUTOMÁTICO TELEGRAM
# ============================

if was_sent:
    send_telegram_alert(trade_signal, sl, tp)
    st.success(f"📬 Alerta enviado automaticamente para: {trade_signal}")
else:
    st.info("⚪ Nenhum alerta enviado. Sinal atual: WAIT.")

# ============================
# 🔄 AUTO-REFRESH 15 MINUTOS
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
# 📊 HISTÓRICO DE SINAIS
# ============================

st.markdown("---")
st.header("📈 Histórico de Sinais")

if os.path.exists("signals_log.csv"):
    df_log = pd.read_csv("signals_log.csv")
    df_log["Timestamp"] = pd.to_datetime(df_log["Timestamp"])

    filtro = st.selectbox("📌 Filtrar por tipo de sinal:", options=["Todos", "BUY", "SELL", "WAIT"])
    if filtro != "Todos":
        df_log = df_log[df_log["Signal"] == filtro]

    st.subheader("🧾 Últimos 20 sinais")
    st.dataframe(df_log.sort_values("Timestamp", ascending=False).head(20), use_container_width=True)

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
    col4.metric("BUY / SELL / WAIT", f"{buy_count} / {sell_count} / {wait_count}")
else:
    st.warning("Nenhum log de sinal encontrado.")

# ============================
# 🧪 BACKTEST COM CAPITAL REAL
# ============================

st.markdown("---")
st.header("🧪 Backtest Simulado (Retorno Real)")

if os.path.exists("signals_log.csv"):
    df_bt = pd.read_csv("signals_log.csv")
    df_bt = df_bt[df_bt["Signal"].isin(["BUY", "SELL"])]
    df_bt["Timestamp"] = pd.to_datetime(df_bt["Timestamp"])

    st.subheader("📈 Curva de Capital")
    st.line_chart(df_bt["Capital"])

    wins = len(df_bt[df_bt["Return (%)"] > 0])
    losses = len(df_bt[df_bt["Return (%)"] < 0])
    total_bt = wins + losses
    winrate = round(wins / total_bt * 100, 2) if total_bt else 0
    capital_final = df_bt["Capital"].iloc[-1] if total_bt else 10000
    capital_inicial = df_bt["Capital"].iloc[0] if total_bt else 10000
    lucro_total = round(capital_final - capital_inicial, 2)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Trades", total_bt)
    col2.metric("Winrate (%)", winrate)
    col3.metric("Lucro Acumulado", f"{lucro_total}")
else:
    st.warning("Sem dados suficientes para backtest.")
