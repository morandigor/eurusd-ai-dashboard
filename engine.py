import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import telegram

# Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

def fetch_eurusd_data():
    url = (
        f"https://api.twelvedata.com/time_series?symbol=EUR/USD&interval=1h&outputsize=120&apikey={TWELVE_DATA_API_KEY}"
    )
    response = requests.get(url)
    data = response.json()

    if "values" not in data:
        raise ValueError("Invalid data returned from Twelve Data API")

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["close"] = pd.to_numeric(df["close"])
    df = df.sort_values("datetime")
    return df

def get_trend_signal(df):
    short_ma = df["close"].rolling(window=5).mean()
    long_ma = df["close"].rolling(window=20).mean()

    if short_ma.iloc[-1] > long_ma.iloc[-1]:
        return "BUY"
    elif short_ma.iloc[-1] < long_ma.iloc[-1]:
        return "SELL"
    else:
        return "NEUTRAL"

def get_sentiment_signal(df):
    recent = df["close"].iloc[-10:]
    if recent.pct_change().mean() > 0:
        return "BUY"
    elif recent.pct_change().mean() < 0:
        return "SELL"
    else:
        return "NEUTRAL"

def generate_trade_signal(trend, sentiment):
    if trend == sentiment:
        return trend
    if trend != "NEUTRAL" and sentiment == "NEUTRAL":
        return trend
    if sentiment != "NEUTRAL" and trend == "NEUTRAL":
        return sentiment
    return "NEUTRAL"

def calculate_sl_tp(df, signal):
    current_price = df["close"].iloc[-1]
    if signal == "BUY":
        stop_loss = round(current_price * 0.99, 5)
        take_profit = round(current_price * 1.01, 5)
    elif signal == "SELL":
        stop_loss = round(current_price * 1.01, 5)
        take_profit = round(current_price * 0.99, 5)
    else:
        stop_loss = round(current_price * 0.995, 5)
        take_profit = round(current_price * 1.005, 5)
    return stop_loss, take_profit

def send_telegram_alert(signal, sl, tp):
    message = (
        f"📢 EUR/USD Trade Signal:\n"
        f"Signal: <b>{signal}</b>\n"
        f"Stop Loss: <b>{sl}</b>\n"
        f"Take Profit: <b>{tp}</b>"
    )
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode=telegram.constants.ParseMode.HTML)

# Optional: auto trigger when this script is run standalone
if __name__ == "__main__":
    df = fetch_eurusd_data()
    trend = get_trend_signal(df)
    sentiment = get_sentiment_signal(df)
    final_signal = generate_trade_signal(trend, sentiment)
    sl, tp = calculate_sl_tp(df, final_signal)
    send_telegram_alert(final_signal, sl, tp)
