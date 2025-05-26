import os
import requests
from datetime import datetime
import pandas as pd
from supabase import create_client, Client

# Load secrets via environment variables
TWELVE_DATA_API_KEY = os.environ.get("TWELVE_DATA_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# === Signal Engine ===
def fetch_eurusd_data():
    url = f"https://api.twelvedata.com/time_series?symbol=EUR/USD&interval=15min&apikey={TWELVE_DATA_API_KEY}&outputsize=100"
    r = requests.get(url)
    data = r.json()
    if "values" not in data:
        raise Exception(f"Erro na API Twelve Data: {data}")
    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")
    df.set_index("datetime", inplace=True)
    df = df.astype(float)
    return df

def get_trend_signal(df):
    df["ema20"] = df["close"].ewm(span=20).mean()
    df["ema50"] = df["close"].ewm(span=50).mean()
    return "uptrend" if df["ema20"].iloc[-1] > df["ema50"].iloc[-1] else "downtrend"

def get_sentiment_signal(df):
    return "bullish" if df["close"].iloc[-1] > df["open"].iloc[-1] else "bearish"

def generate_trade_signal(trend, sentiment):
    if trend == "uptrend" and sentiment == "bullish":
        return "BUY"
    elif trend == "downtrend" and sentiment == "bearish":
        return "SELL"
    return "WAIT"

def calculate_sl_tp_price(signal, price):
    if signal == "BUY":
        return round(price * 0.995, 5), round(price * 1.01, 5)
    elif signal == "SELL":
        return round(price * 1.005, 5), round(price * 0.99, 5)
    return 0, 0

def log_signal(signal, sl, tp, trend, sentiment, entry_price, sent, future_high=None, future_low=None):
    timestamp = datetime.utcnow().isoformat()
    hit = "pending"
    return_pct = 0
    capital = 1000

    if signal == "BUY" and future_high and future_low:
        if future_high >= tp:
            hit = "tp"
            return_pct = 1.0
        elif future_low <= sl:
            hit = "sl"
            return_pct = -0.5
        else:
            hit = "none"
    elif signal == "SELL" and future_high and future_low:
        if future_low <= tp:
            hit = "tp"
            return_pct = 1.0
        elif future_high >= sl:
            hit = "sl"
            return_pct = -0.5
        else:
            hit = "none"

    data = {
        "timestamp": timestamp,
        "signal": signal,
        "sl": sl,
        "tp": tp,
        "trend": trend,
        "sentiment": sentiment,
        "price": entry_price,
        "hit": hit,
        "return_pct": return_pct,
        "capital": capital,
        "sent": sent
    }
    supabase.table("signals_log").insert(data).execute()

def get_logs_from_supabase():
    response = supabase.table("signals_log").select("*").order("timestamp", desc=True).limit(100).execute()
    return pd.DataFrame(response.data)

def log_to_csv(signal, sl, tp, trend, sentiment, entry_price, was_sent, future_high, future_low):
    file = "db/signals_log.csv"
    if os.path.exists(file):
        df = pd.read_csv(file)
    else:
        df = pd.DataFrame(columns=["timestamp", "signal", "sl", "tp", "trend", "sentiment", "price", "hit", "return_pct", "capital", "sent"])

    timestamp = datetime.utcnow().isoformat()
    hit = "none"
    return_pct = 0
    capital = 1000

    if signal == "BUY":
        if future_high >= tp:
            hit = "tp"
            return_pct = 1.0
        elif future_low <= sl:
            hit = "sl"
            return_pct = -0.5
    elif signal == "SELL":
        if future_low <= tp:
            hit = "tp"
            return_pct = 1.0
        elif future_high >= sl:
            hit = "sl"
            return_pct = -0.5

    new_row = {
        "timestamp": timestamp,
        "signal": signal,
        "sl": sl,
        "tp": tp,
        "trend": trend,
        "sentiment": sentiment,
        "price": entry_price,
        "hit": hit,
        "return_pct": return_pct,
        "capital": capital,
        "sent": was_sent
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(file, index=False)
