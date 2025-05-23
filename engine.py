import os
import requests
import pandas as pd
from dotenv import load_dotenv
from telegram import Bot

# Load environment variables from .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TWELVE_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

# 1. Fetch data from Twelve Data API
def fetch_eurusd_data():
    url = f"https://api.twelvedata.com/time_series?symbol=EUR/USD&interval=1h&outputsize=100&apikey={TWELVE_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "values" not in data:
        raise ValueError("Invalid data returned from Twelve Data API")

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")
    df = df.astype({"open": float, "high": float, "low": float, "close": float})
    return df

# 2. Trend signal (based on close vs open)
def get_trend_signal(df):
    return "BUY" if df["close"].iloc[-1] > df["open"].iloc[0] else "SELL" if df["close"].iloc[-1] < df["open"].iloc[0] else "NEUTRAL"

# 3. Sentiment signal (based on average close vs average open)
def get_sentiment_signal(df):
    avg_close = df["close"].mean()
    avg_open = df["open"].mean()
    return "BUY" if avg_close > avg_open else "SELL" if avg_close < avg_open else "NEUTRAL"

# 4. Final signal logic
def generate_trade_signal(trend, sentiment):
    return trend if trend == sentiment else "NEUTRAL"

# 5. SL/TP calculator (based on signal)
def calculate_sl_tp(df, signal):
    current_price = df["close"].iloc[-1]
    if signal == "BUY":
        stop_loss = round(current_price * 0.985, 5)
        take_profit = round(current_price * 1.015, 5)
    elif signal == "SELL":
        stop_loss = round(current_price * 1.015, 5)
        take_profit = round(current_price * 0.985, 5)
    else:
        stop_loss, take_profit = None, None
    return stop_loss, take_profit

# 6. Telegram alert sender
def send_telegram_alert(signal, stop_loss, take_profit):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return

    if signal == "NEUTRAL":
        return

    message = (
        f"📢 <b>EUR/USD Trade Signal:</b>\n"
        f"Signal: <b>{signal}</b>\n"
        f"Stop Loss: <b>{stop_loss}</b>\n"
        f"Take Profit: <b>{take_profit}</b>"
    )
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="HTML")
