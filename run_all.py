from collectors import price, economic_events, cot_report, sentiment, news
from dashboard.engine import generate_trade_signal
from alerts.telegram import send_alert
from dotenv import load_dotenv
import os

# === Load environment variables ===
load_dotenv()

print("Running data collectors...")

# === Data Collection ===
price.fetch_eurusd_candles()
economic_events.fetch_events()
cot_report.fetch_cot()
sentiment.fetch_sentiment()
news.fetch_news()

print("✅ All data collected.")

# === Signal Generation ===
signal = generate_trade_signal()

print("🧠 Signal Engine Results:")
print("🚨 SIGNAL:", signal)

# === Telegram Alert ===
send_alert(f"🚨 EUR/USD SIGNAL: {signal}")
