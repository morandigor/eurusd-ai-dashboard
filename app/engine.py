import pandas as pd
import requests

def fetch_eurusd_data():
    # 🔁 Substituir com sua fonte real (API, CSV, etc.)
    url = "https://api.example.com/eurusd"  # Exemplo
    df = pd.read_csv("sample_data.csv")     # Mock
    df['time'] = pd.to_datetime(df['time'])
    return df

def get_trend_signal(df):
    # Exemplo simples: média móvel
    df['ma'] = df['close'].rolling(10).mean()
    if df['close'].iloc[-1] > df['ma'].iloc[-1]:
        return "uptrend"
    else:
        return "downtrend"

def get_sentiment_signal():
    # Simula análise de sentimento
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
    return round(close * 0.995, 5), round(close * 1.005, 5)  # SL, TP

def log_signal(signal, sl, tp):
    with open("logs.txt", "a") as f:
        f.write(f"{signal} | SL: {sl} | TP: {tp}\n")
