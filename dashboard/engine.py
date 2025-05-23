import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

LOG_PATH = "db/signals_log.csv"


def get_trend_signal(df):
    return "NEUTRAL" if df['close'].iloc[-1] == df['close'].iloc[-2] else (
        "BUY" if df['close'].iloc[-1] > df['close'].iloc[-2] else "SELL"
    )


def get_sentiment_signal(df):
    return "BUY" if df['open'].iloc[-1] < df['close'].iloc[-1] else "SELL"


def get_final_signal(trend, sentiment):
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


def log_signal(timestamp, signal, sl, tp, result="pending"):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    file_exists = os.path.isfile(LOG_PATH)

    with open(LOG_PATH, mode="a", newline="") as file:
        writer = pd.io.common.csv_writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "signal", "stop_loss", "take_profit", "result"])
        writer.writerow([timestamp, signal, sl, tp, result])


def generate_trade_signal(df):
    trend = get_trend_signal(df)
    sentiment = get_sentiment_signal(df)
    final = get_final_signal(trend, sentiment)
    price = df['close'].iloc[-1]
    sl, tp = calculate_sl_tp(price, final)
    return final, sl, tp