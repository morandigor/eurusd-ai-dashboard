from app.engine import (
    fetch_eurusd_data,
    get_trend_signal,
    get_sentiment_signal,
    generate_trade_signal,
    calculate_sl_tp,
    log_to_supabase
)
from app.telegram import send_telegram_alert
from datetime import datetime, timezone

# 📥 Coleta dados
df = fetch_eurusd_data()

# 🧠 Calcula sinais
trend = get_trend_signal(df)
sentiment = get_sentiment_signal(df)
signal = generate_trade_signal(trend, sentiment, df)
# 💰 Preço atual
current_price = df["close"].iloc[-1]

# 🛡️ SL e TP
sl, tp = calculate_sl_tp(df, signal)

# 🕒 Timestamp atual em UTC
timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

# 📤 Envia alerta no Telegram (apenas se for BUY ou SELL)
if signal in ["BUY", "SELL"]:
    msg = f"""
📈 Novo sinal gerado: {signal}
💰 Entrada: {current_price:.5f}
🛑 SL: {sl:.5f} | 🎯 TP: {tp:.5f}
🕒 {timestamp} UTC
"""
    send_telegram_alert(msg, sl, tp)

# 🧾 Loga no Supabase
log_to_supabase(
    signal=signal,
    sl=sl,
    tp=tp,
    trend=trend,
    sentiment=sentiment,
    price=current_price,
    hit="-",
    return_pct=0.0,
    capital=0.0,
    sent="auto"
)
