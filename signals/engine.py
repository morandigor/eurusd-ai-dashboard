import sqlite3
import pandas as pd

def get_trend_signal():
    conn = sqlite3.connect('db/database.db')
    df = pd.read_sql_query("SELECT * FROM eurusd_prices ORDER BY timestamp DESC LIMIT 20", conn)
    conn.close()

    if df.empty or len(df) < 5:
        return "Unknown"

    df = df.sort_values("timestamp")
    df["close"] = df["close"].astype(float)

    slope = df["close"].diff().mean()

    if slope > 0.00015:
        return "Strong Uptrend"
    elif slope < -0.00015:
        return "Strong Downtrend"
    else:
        return "Sideways / Weak"
def get_cot_bias():
    conn = sqlite3.connect('db/database.db')
    df = pd.read_sql_query("SELECT * FROM cot_reports ORDER BY report_date DESC LIMIT 2", conn)
    conn.close()

    if df.empty or len(df) < 2:
        return "Unknown"

    delta_long = df["non_commercial_long"].iloc[0] - df["non_commercial_long"].iloc[1]
    delta_short = df["non_commercial_short"].iloc[0] - df["non_commercial_short"].iloc[1]

    if delta_long > 0 and delta_short <= 0:
        return "Smart Money Buying"
    elif delta_short > 0 and delta_long <= 0:
        return "Smart Money Selling"
    else:
        return "Neutral / No Clear Flow"
def get_sentiment_signal():
    conn = sqlite3.connect('db/database.db')
    df = pd.read_sql_query("SELECT * FROM sentiment_data ORDER BY timestamp DESC LIMIT 1", conn)
    conn.close()

    if df.empty:
        return "Unknown"

    long_pct = df["long_percent"].iloc[0]
    short_pct = df["short_percent"].iloc[0]

    if long_pct >= 75:
        return "High Risk - Retail Long Crowded"
    elif short_pct >= 75:
        return "High Risk - Retail Short Crowded"
    else:
        return "Balanced Sentiment"
def generate_trade_signal():
    trend = get_trend_signal()
    bias = get_cot_bias()
    sentiment = get_sentiment_signal()

    print("🧠 Trend:", trend)
    print("💰 Smart Money:", bias)
    print("⚠️ Sentiment Risk:", sentiment)

    if "Uptrend" in trend and "Buying" in bias and "Balanced" in sentiment:
        return "✅ BUY SETUP"
    elif "Downtrend" in trend and "Selling" in bias and "Balanced" in sentiment:
        return "🔻 SELL SETUP"
    else:
        return "⏸ WAIT / NO CLEAR EDGE"
