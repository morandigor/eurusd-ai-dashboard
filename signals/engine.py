import requests
import pandas as pd
from datetime import datetime
import pytz
import os

# === Constants ===
API_KEY = os.getenv("TWELVE_DATA_API_KEY")  # Make sure to set this in your Streamlit secret or env
TG_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# === Fetch Price Data ===
def fetch_price_data():
    url = (
        f"https://api.twelvedata.com/time_series?symbol=EUR/USD"
        f"&interval=1day&outputsize=5&apikey={API_KEY}"
    )
    response = requests.get(url)
    data = response.json()

    if "values" not in data:
        raise ValueError("Invalid data returned from Twelve Data API")

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["close"] = df["close"].astype(float)
    df.sort_values("datetime", inplace=True)

    return df

# === Signal Engines ===
def get_trend_signal(df: pd.DataFrame) -> str:
    last_two = df.tail(2)["close"].values
    return "BUY" if last_two[1] > last_two[0] else "SELL"

def get_sentiment_signal() -> str:
    # Placeholder for real sentiment (e.g., news sentiment API)
    # For now, we simulate with dummy logic
    hour = datetime.now(pytz.timezone("Europe/London")).hour
    return "BUY" if 8 <= hour <= 16 else "SELL"

def generate_trade_signal(trend: str, sentiment: str) -> str:
    if trend == sentiment:
        return trend
    return "NEUTRAL"

# === Alert ===
def send_alert(message: str):
    if not TG_TOKEN or not TG_CHAT_ID:
        print("Telegram credentials not set.")
        return

    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": TG_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)
