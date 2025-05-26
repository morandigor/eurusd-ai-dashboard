import requests
import streamlit as st

def send_telegram_alert(signal, sl, tp):
    token = st.secrets["TELEGRAM_BOT_TOKEN"]
    chat_id = st.secrets["TELEGRAM_CHAT_ID"]

    emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "⚪️"
    message = (
        f"{emoji} *EUR/USD Trade Signal*\n\n"
        f"*Signal:* `{signal}`\n"
        f"*Stop Loss:* `{sl}`\n"
        f"*Take Profit:* `{tp}`"
    )

    url = (
        f"https://api.telegram.org/bot{token}/sendMessage?"
        f"chat_id={chat_id}&text={message}&parse_mode=Markdown"
    )

    response = requests.get(url)
    if not response.ok:
        st.error(f"❌ Erro ao enviar alerta: {response.text}")
