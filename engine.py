import os
import csv
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
LOG_PATH = "dashboard/data/signals_log.csv"

def fetch_eurusd_data():
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": "EUR/USD",
        "interval": "1h",
        "outputsize": 100,
        "apikey": os.getenv("TWELVE_DATA_API_KEY")
    }
    response = requests.get(url, params=params)
    data = response.json()

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")
    df["close"] = pd.to_numeric(df["close"])

    return df

def get_trend_signal(df):
    recent = df["close"].iloc[-5:]
    if recent.is_monotonic_increasing:
        return "BUY"
    elif recent.is_monotonic_decreasing:
        return "SELL"
    return "NEUTRAL"

def get_sentiment_signal(df):
    change = df["close"].pct_change().iloc[-5:]
    sentiment = "BUY" if change.mean() > 0 else "SELL"
    return sentiment

def calculate_sl_tp(price, signal):
    price = float(price)
    if signal == "BUY":
        return round(price * 0.99, 5), round(price * 1.02, 5)
    elif signal == "SELL":
        return round(price * 1.01, 5), round(price * 0.98, 5)
    return None, None

def log_signal(timestamp, signal, sl, tp, result="pending"):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    file_exists = os.path.isfile(LOG_PATH)

    with open(LOG_PATH, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "signal", "stop_loss", "take_profit", "result"])
        writer.writerow([timestamp, signal, sl, tp, result])

def send_telegram_alert(signal, stop_loss, take_profit):
    if TELEGRAM_TOKEN and CHAT_ID:
        bot = Bot(token=TELEGRAM_TOKEN)
        msg = (
            f"📢 EUR/USD Trade Signal:\n"
            f"Signal: {signal}\n"
            f"Stop Loss: {stop_loss}\n"
            f"Take Profit: {take_profit}"
        )
        bot.send_message(chat_id=CHAT_ID, text=msg)

def run_signal_engine():
    df = fetch_eurusd_data()
    trend = get_trend_signal(df)
    sentiment = get_sentiment_signal(df)

    final_signal = trend if trend == sentiment else "NEUTRAL"
    latest_price = df["close"].iloc[-1]
    sl, tp = calculate_sl_tp(latest_price, final_signal)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_signal(timestamp, final_signal, sl, tp)
    send_telegram_alert(final_signal, sl, tp)

    return final_signal, trend, sentiment, sl, tp
