import pandas as pd
from datetime import datetime
import os

LOG_PATH = "db/signals_log.csv"

def fetch_eurusd_data():
    # Simulated data - replace with your real source/API call
    now = pd.Timestamp.now()
    data = {
        "timestamp": pd.date_range(end=now, periods=60, freq="H"),
        "price": [1.12 + 0.0001 * i for i in range(60)]
    }
    return pd.DataFrame(data)

def get_trend_signal(df):
    return "BUY" if df['price'].iloc[-1] > df['price'].iloc[-10] else "SELL"

def get_sentiment_signal(df):
    return "BUY" if df['price'].diff().mean() > 0 else "SELL"

def generate_trade_signal(trend, sentiment):
    return "BUY" if trend == "BUY" and sentiment == "BUY" else "SELL"

def calculate_sl_tp_price(price, signal, sl_multiplier, tp_multiplier):
    if signal == "BUY":
        return price * sl_multiplier, price * tp_multiplier
    elif signal == "SELL":
        return price / tp_multiplier, price / sl_multiplier
    return None, None

def log_signal(timestamp, signal, sl, tp):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    file_exists = os.path.isfile(LOG_PATH)
    with open(LOG_PATH, mode="a") as f:
        if not file_exists:
            f.write("timestamp,signal,sl,tp\n")
        f.write(f"{timestamp},{signal},{sl},{tp}\n")
