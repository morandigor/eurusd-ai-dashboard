import pandas as pd
import requests
import os
from datetime import datetime

def fetch_eurusd_data():
    # 🔐 Pega a API Key do .env
    api_key = os.getenv("TWELVE_DATA_API_KEY")

    # 🔗 Endpoint da Twelve Data para EUR/USD (intervalo de 1h)
    url = (
        f"https://api.twelvedata.com/time_series?"
        f"symbol=EUR/USD&interval=1h&outputsize=100&apikey={api_key}"
    )

    response = requests.get(url)
    data = response.json()

    if "values" not in data:
        raise Exception(f"Erro ao buscar dados da Twelve Data: {data}")

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

    df = df.sort_values("time")  # Garante ordem cronológica crescente
    return df

def get_trend_signal(df):
    df['ma'] = df['close'].rolling(10).mean()
    if df['close'].iloc[-1] > df['ma'].iloc[-1]:
        return "uptrend"
    else:
        return "downtrend"

def get_sentiment_signal():
    # Placeholder fixo
    return "bullish"

def generate_trade_signal(trend, sentiment):
    if trend == "uptrend" and sentiment == "bullish":
        return "BUY"
    elif trend == "downtrend" and sentiment == "bearish":
        return "SELL"
    else:
        return "WAIT"

def calculate_sl_tp_price(df):
    close = df['close'].iloc[-1]
    sl = round(close * 0.995, 5)
    tp = round(close * 1.005, 5)
    return sl, tp

def log_signal(signal, sl, tp):
    with open("logs.txt", "a") as f:
        f.write(f"{datetime.now()} | {signal} | SL: {sl} | TP: {tp}\n")
