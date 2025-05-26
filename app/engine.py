import streamlit as st
import pandas as pd
import requests
from datetime import datetime

def fetch_eurusd_data():
    api_key = st.secrets["TWELVE_DATA_API_KEY"]

    url = (
        f"https://api.twelvedata.com/time_series?"
        f"symbol=EUR/USD&interval=1h&outputsize=100&apikey={api_key}"
    )

    response = requests.get(url)
    data = response.json()

    if "values" not in data:
        st.error("❌ Erro ao buscar dados na Twelve Data")
        st.json(data)
        st.stop()

    df = pd.DataFrame(data["values"])
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.rename(columns={
        "datetime": "time",
        "open": "open",
        "high": "high",
        "low": "low",
        "close": "close"
    })
    df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].astype(float)
    df = df.sort_values("time")
    return df


def get_trend_signal(df):
    df['ma'] = df['close'].rolling(10).mean()
    return "uptrend" if df['close'].iloc[-1] > df['ma'].iloc[-1] else "downtrend"

def get_sentiment_signal():
    return "bullish"  # placeholder

def generate_trade_signal(trend, sentiment):
    if trend == "uptrend" and sentiment == "bullish":
        return "BUY"
    elif trend == "downtrend" and sentiment == "bearish":
        return "SELL"
    return "WAIT"

def calculate_sl_tp_price(df):
    close = df['close'].iloc[-1]
    return round(close * 0.995, 5), round(close * 1.005, 5)

def log_signal(signal, sl, tp):
    with open("logs.txt", "a") as f:
        f.write(f"{datetime.now()} | {signal} | SL: {sl} | TP: {tp}\n")
