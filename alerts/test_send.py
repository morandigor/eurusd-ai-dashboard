import requests
import os
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

url = f"https://api.telegram.org/bot{token}/sendMessage"
payload = {
    "chat_id": chat_id,
    "text": "✅ This is a test message from your EUR/USD signal bot."
}

response = requests.post(url, data=payload)
print("Status Code:", response.status_code)
print("Response:", response.text)