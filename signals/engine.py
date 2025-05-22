import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz

# Telegram Config (you must set these in Streamlit secrets)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Telegram alert failed: {e}")

def fetch_eurusd_data():
    api_key = os.getenv("TWELVE_DATA_API_KEY")
    url = f"https://api.twelvedata.com/time_series?symbol=EUR/USD&interval=1day&outputsize=30&apikey={api_key}"
    response = requests.get(url)
    data = response.json()

    if "values" not in data:
        raise ValueError("Invalid data returned from Twelve Data API")

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["close"] = pd.to_numeric(df["close"])
    df = df.sort_values("datetime").reset_index(drop=True)
    return df

def get_trend_signal(df):
    df["sma_3"] = df["close"].rolling(window=3).mean()
    df["sma_5"] = df["close"].rolling(window=5).mean()

    if df["sma_3"].iloc[-1] > df["sma_5"].iloc[-1]:
        return "BUY"
    elif df["sma_3"].iloc[-1] < df["sma_5"].iloc[-1]:
        return "SELL"
    return "NEUTRAL"

def get_sentiment_signal(df):
    if df["close"].iloc[-1] > df["close"].iloc[-2]:
        return "BUY"
    elif df["close"].iloc[-1] < df["close"].iloc[-2]:
        return "SELL"
    return "NEUTRAL"

def generate_trade_signal(trend, sentiment):
    if trend == sentiment:
        return trend
    return "NEUTRAL"

def calculate_sl_tp(last_close, direction):
    if direction == "BUY":
        sl = round(last_close * 0.995, 5)
        tp = round(last_close * 1.005, 5)
    elif direction == "SELL":
        sl = round(last_close * 1.005, 5)
        tp = round(last_close * 0.995, 5)
    else:
        sl = tp = None
    return sl, tp

def evaluate_and_alert():
    df = fetch_eurusd_data()
    trend = get_trend_signal(df)
    sentiment = get_sentiment_signal(df)
    final_signal = generate_trade_signal(trend, sentiment)

    last_price = df["close"].iloc[-1]
    sl, tp = calculate_sl_tp(last_price, final_signal)

    if final_signal in ["BUY", "SELL"]:
        msg = f"🚨 EUR/USD Signal: {final_signal}\nEntry: {last_price}\nSL: {sl}\nTP: {tp}"
        send_telegram_message(msg)

    return trend, sentiment, final_signal, df
