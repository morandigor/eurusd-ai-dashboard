import requests
import pandas as pd
from datetime import datetime, timedelta
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# 📦 API Twelve Data
TWELVE_API_KEY = os.getenv("TWELVEDATA_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# ✅ Inicializa Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_eurusd_data():
    url = f"https://api.twelvedata.com/time_series?symbol=EUR/USD&interval=1h&outputsize=500&apikey={TWELVE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    if "values" in data:
        df = pd.DataFrame(data["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("datetime")
        df = df.astype({"open": float, "high": float, "low": float, "close": float})
        return df
    else:
        raise Exception(f"Erro na API Twelve Data: {data}")

def get_trend_signal(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    return "uptrend" if last["close"] > prev["close"] else "downtrend"

def get_sentiment_signal(df):
    last = df.iloc[-1]
    if last["close"] > last["open"]:
        return "bullish"
    elif last["close"] < last["open"]:
        return "bearish"
    else:
        return "neutral"

def get_trade_signal(trend, sentiment):
    if trend == "uptrend" and sentiment == "bullish":
        return "BUY"
    elif trend == "downtrend" and sentiment == "bearish":
        return "SELL"
    else:
        return "WAIT"

def calculate_sl_tp(df, signal):
    if signal == "BUY":
        sl = round(df.iloc[-1]["low"], 5)
        tp = round(df.iloc[-1]["high"] + (df.iloc[-1]["high"] - sl), 5)
    elif signal == "SELL":
        tp = round(df.iloc[-1]["low"], 5)
        sl = round(df.iloc[-1]["high"] + (df.iloc[-1]["high"] - tp), 5)
    else:
        sl = tp = 0
    return sl, tp

def log_to_supabase(trade_signal, sl, tp, trend, sentiment, price, hit, return_pct, capital, sent):
    data = {
        "timestamp": datetime.utcnow().isoformat(),
        "signal_text": trade_signal,
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

def get_logs_from_supabase():
    response = supabase.table("signals_log").select("*").order("timestamp", desc=True).limit(100).execute()
    return response.data
