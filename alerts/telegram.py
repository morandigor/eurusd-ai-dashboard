import requests
import os
from dotenv import load_dotenv

load_dotenv()

def send_alert(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("✅ Telegram alert sent.")
    else:
        print("❌ Failed to send alert:", response.text)
