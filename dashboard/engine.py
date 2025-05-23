import csv
import os
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
LOG_PATH = "db/signals_log.csv"

def fetch_eurusd_data():
    url = "https://api.twelvedata.com/time_series?symbol=EUR/USD&interval=1h&apikey=" + os.getenv("TWELVE_DATA_API_KEY")
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")
    df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].astype(float)
    return df

def get_trend_signal(df):
    recent_change = df["close"].pct_change().iloc[-5:].sum()
    return "BUY" if recent_change > 0 else "SELL"

def get_sentiment_signal():
    # Simulated sentiment signal for now
    return "BUY" if datetime.utcnow().minute % 2 == 0 else "SELL"

def generate_trade_signal(trend, sentiment):
    if trend == sentiment:
        return trend
    return "NEUTRAL"

def calculate_sl_tp(price, signal):
    price = float(price)
    if signal == "BUY":
        return round(price * 0.99, 5), round(price * 1.02, 5)
    elif signal == "SELL":
        return round(price * 1.01, 5), round(price * 0.98, 5)
    return None, None

def send_telegram_alert(signal, stop_loss, take_profit):
    message = (
        "📢 EUR/USD Trade Signal:\n"
        f"Signal: {signal}\n"
        f"Stop Loss: <b>{stop_loss}</b>\n"
        f"Take Profit: <b>{take_profit}</b>"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)

def log_signal(timestamp, signal, sl, tp, result="pending"):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    file_exists = os.path.isfile(LOG_PATH)

    with open(LOG_PATH, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "signal", "stop_loss", "take_profit", "result"])
        writer.writerow([timestamp, signal, sl, tp, result])

