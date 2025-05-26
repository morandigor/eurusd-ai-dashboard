import requests
import os

def send_telegram_alert(signal, sl, tp):
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    message = (
        f"📢 *EUR/USD Trade Signal*\n"
        f"Signal: *{signal}*\n"
        f"Stop Loss: `{sl}`\n"
        f"Take Profit: `{tp}`"
    )

    url = (
        f"https://api.telegram.org/bot{token}/sendMessage?"
        f"chat_id={chat_id}&text={message}&parse_mode=Markdown"
    )

    response = requests.get(url)
    if not response.ok:
        raise Exception(f"Telegram error: {response.text}")
