import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Twelve Data API
API_KEY = os.getenv("TWELVEDATA_API_KEY")

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_eurusd_data():
    url = f"https://api.twelvedata.com/time_series?symbol=EUR/USD&interval=15min&outputsize=100&apikey={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "values" not in data:
        raise Exception(f"Erro na API Twelve Data: {data}")

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")
    df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].astype(float)
    df = df.set_index("datetime")
    return df

def get_trend_signal(df):
    df["ema_fast"] = df["close"].ewm(span=8).mean()
    df["ema_slow"] = df["close"].ewm(span=21).mean()
    if df["ema_fast"].iloc[-1] > df["ema_slow"].iloc[-1]:
        return "uptrend"
    else:
        return "downtrend"

def get_sentiment_signal(df):
    df["rsi"] = compute_rsi(df["close"], 14)
    if df["rsi"].iloc[-1] > 60:
        return "bullish"
    elif df["rsi"].iloc[-1] < 40:
        return "bearish"
    else:
        return "neutral"

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_sl_tp(df, signal):
    atr = df["high"].rolling(window=14).max() - df["low"].rolling(window=14).min()
    atr_value = atr.iloc[-1]
    last_price = df["close"].iloc[-1]

    if signal == "BUY":
        sl = last_price - atr_value
        tp = last_price + 2 * atr_value
    elif signal == "SELL":
        sl = last_price + atr_value
        tp = last_price - 2 * atr_value
    else:
        sl, tp = 0, 0

    return round(sl, 5), round(tp, 5)

def generate_trade_signal(df, trend_signal, sentiment_signal):
    if trend_signal == "uptrend" and sentiment_signal == "bullish":
        return "BUY"
    elif trend_signal == "downtrend" and sentiment_signal == "bearish":
        return "SELL"
    else:
        return "WAIT"

def log_to_supabase(signal, sl, tp, trend, sentiment, price, hit, return_pct, capital, sent):
    now = datetime.utcnow().isoformat()
    data = {
        "timestamp": now,
        "signal": signal,
        "sl": sl,
        "tp": tp,
        "trend": trend,
        "sentiment": sentiment,
        "price": price,
        "hit": hit,
        "return_pct": return_pct,
        "capital": capital,
        "sent": sent
    }
    supabase.table("signals_log").insert(data).execute()

__all__ = [
    "fetch_eurusd_data",
    "get_trend_signal",
    "get_sentiment_signal",
    "calculate_sl_tp",
    "generate_trade_signal",
    "log_to_supabase"
]
