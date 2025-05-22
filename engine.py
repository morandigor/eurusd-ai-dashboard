import os
import requests
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()
TELEGRAM_TOKEN = st.secrets["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]

# === Signal cache ===
last_sent_signal = {"type": None, "time": None}


# === Fetch price data ===
def fetch_price_data():
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": "EUR/USD",
        "interval": "1h",
        "outputsize": 120,
        "apikey": st.secrets["TWELVE_DATA_API_KEY"]
    }
    response = requests.get(url, params=params)
    data = response.json()
    return pd.DataFrame(data["values"])


# === Generate signal ===
def generate_trade_signal(trend, sentiment):
    if trend == "BUY" and sentiment == "BUY":
        return "BUY"
    elif trend == "SELL" and sentiment == "SELL":
        return "SELL"
    else:
        return "NEUTRAL"


# === Calculate SL/TP (Simple version) ===
def calculate_sl_tp(df, signal):
    last_close = float(df.iloc[0]["close"])
    if signal == "BUY":
        sl = last_close * 0.995  # -0.5%
        tp = last_close * 1.01   # +1%
    elif signal == "SELL":
        sl = last_close * 1.005  # +0.5%
        tp = last_close * 0.99   # -1%
    else:
        sl, tp = None, None
    return round(sl, 5), round(tp, 5)


# === Send Telegram Alert if it's BUY or SELL only ===
def send_telegram_alert(signal, sl, tp):
    global last_sent_signal

    now = datetime.utcnow()
    should_send = False

    if signal in ["BUY", "SELL"]:
        if last_sent_signal["type"] != signal:
            should_send = True
        elif last_sent_signal["time"] is None or (now - last_sent_signal["time"]).seconds >= 3600:
            should_send = True

    if should_send:
        message = (
            f"📢 EUR/USD Trade Signal:\n"
            f"Signal: *{signal}*\n"
            f"Stop Loss: *{sl}*\n"
            f"Take Profit: *{tp}*"
        )
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        requests.post(url, data=payload)

        last_sent_signal["type"] = signal
        last_sent_signal["time"] = now
