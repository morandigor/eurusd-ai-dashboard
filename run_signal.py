import pandas as pd
from app.engine import (
    fetch_eurusd_data,
    get_trend_signal,
    get_sentiment_signal,
    generate_trade_signal,
    calculate_sl_tp,
    log_to_supabase
)
from app.telegram import send_telegram_alert
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# 🚀 Coleta dados
df = fetch_eurusd_data()

# 🧠 Sinais
trend = get_trend_signal(df)
sentiment = get_sentiment_signal(df)
signal = generate_trade_signal(trend, sentiment, df)


# 💰 Preço atual
current_price = df["close"].iloc[-1]

# 🛡️ SL e TP
sl, tp = calculate_sl_tp(df, signal)

# 🕒 Timestamp
timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

# 📤 Mensagem Telegram
msg = f"""📉 EUR/USD AI SIGNAL
Sinal: {signal}
Timestamp: {timestamp}
"""

if signal in ["BUY", "SELL"]:
    msg += f"SL: {sl:.5f}\nTP: {tp:.5f}"
    send_telegram_alert(msg, sl, tp)
else:
    send_telegram_alert(msg, sl=0, tp=0)

# 🧾 Loga no Supabase (simulando valores neutros para retorno/capital)
log_to_supabase(
    signal=signal,
    sl=sl,
    tp=tp,
    trend=trend,
    sentiment=sentiment,
    price=current_price,
    hit="",
    return_pct=0,
    capital=0,
    sent="yes"
)
