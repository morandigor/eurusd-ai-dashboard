import os
import requests
import pandas as pd

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def fetch_data():
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": "EUR/USD",
        "interval": "1day",
        "apikey": os.getenv("TWELVE_DATA_API_KEY"),
        "outputsize": 5,
    }
    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") != "ok":
        raise ValueError("Invalid data returned from Twelve Data API")

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["close"] = pd.to_numeric(df["close"])
    return df.sort_values("datetime")


def get_trend_signal(df):
    if df["close"].iloc[-1] > df["close"].iloc[0]:
        return "BUY"
    else:
        return "SELL"


def get_sentiment_signal(df):
    change = df["close"].pct_change().mean()
    return "BUY" if change > 0 else "SELL"


def generate_trade_signal(trend, sentiment):
    if trend == sentiment:
        return trend
    return "NEUTRAL"


def send_telegram_alert(signal, entry_price, sl, tp):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return

    message = f"\ud83d\udd39 Trade Alert: {signal}\nEntry: {entry_price}\nSL: {sl}\nTP: {tp}"
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, data=payload)
