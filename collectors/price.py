import requests
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TWELVEDATA_API_KEY")

def fetch_eurusd_candles():
    print("🔄 Running fetch_eurusd_candles")
    url = "https://api.twelvedata.com/time_series"
    params = {
        "symbol": "EUR/USD",
        "interval": "5min",
        "apikey": API_KEY,
        "outputsize": 30
    }
    response = requests.get(url, params=params)
    data = response.json()

    candles = data.get('values', [])
    conn = sqlite3.connect('db/database.db')
    cursor = conn.cursor()

    for candle in candles:
        cursor.execute("""
            INSERT OR IGNORE INTO eurusd_prices 
            (timestamp, open, high, low, close, volume) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            candle['datetime'],
            float(candle['open']),
            float(candle['high']),
            float(candle['low']),
            float(candle['close']),
            float(candle.get('volume', 0))
        ))

    conn.commit()
    conn.close()
