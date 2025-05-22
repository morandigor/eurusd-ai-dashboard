import os
import requests
import pandas as pd

# ENV VARS (from Streamlit secrets or local .env)
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# === Fetch data ===
def fetch_eurusd_data():
    url = f"https://api.twelvedata.com/time_series?symbol=EUR/USD&interval=1h&outputsize=100&apikey={TWELVE_DATA_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if "values" not in data:
        raise ValueError("Invalid data returned from Twelve Data API")
    
    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")
    df["close"] = df["close"].astype(float)
    return df

# === Signal Calculations ===
def get_trend_signal(df):
    short_ma = df["close"].rolling(window=3).mean()
    long_ma = df["close"].rolling(window=12).mean()
    if short_ma.iloc[-1] > long_ma.iloc[-1]:
        return "BUY"
    elif short_ma.iloc[-1] < long_ma.iloc[-1]:
        return "SELL"
    else:
        return "NEUTRAL"

def get_sentiment_signal(df):
    last_candle = df.iloc[-1]
    if float(last_candle["close"]) > float(last_candle["open"]):
        return "BUY"
    elif float(last_candle["close"]) < float(last_candle["open"]):
        return "SELL"
    else:
        return "NEUTRAL"

def generate_trade_signal(trend, sentiment):
    if trend == "BUY" and sentiment == "BUY":
        return "BUY"
    elif trend == "SELL" and sentiment == "SELL":
        return "SELL"
    else:
        return "NEUTRAL"

# === Alert Function ===
def send_telegram_alert(final_signal, sl=None, tp=None):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    message = f"📢 *EUR/USD Trade Signal:*\nSignal: *{final_signal}*"
    if sl and tp:
        message += f"\nStop Loss: `{sl}`\nTake Profit: `{tp}`"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, data=payload)
