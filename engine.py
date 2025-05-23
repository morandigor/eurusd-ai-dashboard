import os
import requests
import pandas as pd
from dotenv import load_dotenv
from telegram import Bot

# Load environment variables from .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def fetch_eurusd_data():
    url = f"https://api.twelvedata.com/time_series?symbol=EUR/USD&interval=1h&outputsize=100&apikey={os.getenv('TWELVE_DATA_API_KEY')}"
    response = requests.get(url)
    data = response.json()

    if "values" not in data:
        raise ValueError("Invalid data returned from Twelve Data API")

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")
    df = df.astype({"open": "float", "high": "float", "low": "float", "close": "float"})

    return df

def get_trend_signal(df):
    if df["close"].iloc[-1] > df["close"].iloc[0]:
        return "BUY"
    elif df["close"].iloc[-1] < df["close"].iloc[0]:
        return "SELL"
    else:
        return "NEUTRAL"

def get_sentiment_signal(df):
    if df["close"].mean() > df["open"].mean():
        return "BUY"
    elif df["close"].mean() < df["open"].mean():
        return "SELL"
    else:
        return "NEUTRAL"

def generate_trade_signal(trend, sentiment):
    if trend == sentiment:
        return trend
    else:
        return "NEUTRAL"

def calculate_sl_tp(df, signal):
    current_price = df["close"].iloc[-1]
    if signal == "BUY":
        stop_loss = current_price * 0.985
        take_profit = current_price * 1.015
    elif signal == "SELL":
        stop_loss = current_price * 1.015
        take_profit = current_price * 0.985
    else:
        stop_loss = None
        take_profit = None
    return round(stop_loss, 5), round(take_profit, 5)

def send_telegram_alert(signal, stop_loss, take_profit):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return

    if signal not in ["BUY", "SELL"]:
        return

    message = f"📢 EUR/USD Trade Signal:\nSignal: {signal}\nStop Loss: <b>{stop_loss}</b>\nTake Profit: <b>{take_profit}</b>"
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="HTML")
