import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import requests
from datetime import datetime

st.set_page_config(page_title="EUR/USD AI Dashboard", layout="wide")
st.title("📊 EUR/USD Trading Intelligence Dashboard")

# --- Telegram Config ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY = os.getenv("TWELVE_DATA_API_KEY")

# --- Constants ---
TICKER = "EUR/USD"
INTERVAL = "1day"
LIMIT = 5


def send_telegram_alert(message):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, data=payload)


def fetch_price_data():
    url = f"https://api.twelvedata.com/time_series?symbol={TICKER}&interval={INTERVAL}&apikey={API_KEY}&outputsize={LIMIT}"
    response = requests.get(url)
    data = response.json()

    if "values" not in data:
        raise ValueError("Invalid data returned from Twelve Data API")

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["close"] = df["close"].astype(float)
    return df.sort_values("datetime").set_index("datetime")


def get_trend_signal(df):
    if df["close"].iloc[-1] > df["close"].mean():
        return "BUY"
    elif df["close"].iloc[-1] < df["close"].mean():
        return "SELL"
    return "NEUTRAL"


def get_sentiment_signal(df):
    change = df["close"].pct_change().iloc[-1]
    if change > 0.002:
        return "BUY"
    elif change < -0.002:
        return "SELL"
    return "NEUTRAL"


def calculate_sl_tp(current_price):
    sl = round(current_price * 0.997, 5)  # -0.3%
    tp = round(current_price * 1.003, 5)  # +0.3%
    return sl, tp


def run_signal_engine():
    df = fetch_price_data()
    trend = get_trend_signal(df)
    sentiment = get_sentiment_signal(df)
    current_price = df["close"].iloc[-1]
    final_signal = trend if trend == sentiment else "NEUTRAL"

    sl, tp = calculate_sl_tp(current_price)

    if final_signal in ["BUY", "SELL"]:
        alert_msg = f"\ud83d\udea8 EUR/USD Signal: {final_signal}\nPrice: {current_price}\nSL: {sl}\nTP: {tp}"
        send_telegram_alert(alert_msg)

    return {
        "chart": df,
        "trend": trend,
        "sentiment": sentiment,
        "final": final_signal,
        "stop_loss": sl,
        "take_profit": tp,
        "error": None
    }