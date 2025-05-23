# engine.py

import pandas as pd
import os
import csv

LOG_PATH = "signals_log.csv"

def fetch_eurusd_data():
    # Replace with real-time or API call
    dates = pd.date_range(end=pd.Timestamp.now(), periods=100, freq="H")
    prices = pd.Series(1.12 + (pd.Series(range(100)) * 0.0001))
    return pd.DataFrame({"datetime": dates, "close": prices})

def get_trend_signal(df):
    change = df['close'].pct_change().iloc[-5:]
    return "BUY" if change.mean() > 0 else "SELL"

def get_sentiment_signal():
    # Stub - replace with real sentiment analysis
    return "BUY"

def generate_trade_signal(trend, sentiment, override="None"):
    if override != "None":
        return override
    if trend == sentiment:
        return trend
    return "NEUTRAL"

def calculate_sl_tp_price(price, signal, sl_multiplier, tp_multiplier):
    if signal == "BUY":
        return round(price * sl_multiplier, 5), round(price * tp_multiplier, 5)
    elif signal == "SELL":
        return round(price * tp_multiplier, 5), round(price * sl_multiplier, 5)
    return None, None

def log_signal(timestamp, signal, sl, tp):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    file_exists = os.path.isfile(LOG_PATH)
    
    with open(LOG_PATH, mode="a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "signal", "stop_loss", "take_profit"])
        writer.writerow([timestamp, signal, sl, tp])
