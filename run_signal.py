import time
from app.engine import (
    fetch_eurusd_data,
    get_trend_signal,
    get_sentiment_signal,
    generate_trade_signal,
    calculate_sl_tp_price,
    log_signal,
)

from app.telegram import send_telegram_alert

try:
    # 1. Coleta de dados
    df = fetch_eurusd_data()
    trend_signal = get_trend_signal(df)
    sentiment_signal = get_sentiment_signal(df)
    trade_signal = generate_trade_signal(trend_signal, sentiment_signal)
    entry_price = df["close"].iloc[-1]
    sl, tp = calculate_sl_tp_price(trade_signal, entry_price)

    # 2. Simula candle futuro
    future_high = entry_price * 1.012
    future_low = entry_price * 0.988

    # 3. Envia alerta se for BUY ou SELL
    was_sent = "no"
    if trade_signal in ["BUY", "SELL"]:
        msg = (
            f"🚨 Sinal Gerado: {trade_signal}\n\n"
            f"📈 Tendência: {trend_signal}\n"
            f"🧠 Sentimento: {sentiment_signal}\n"
            f"🎯 Entrada: {entry_price}\n"
            f"📍 SL: {sl} | TP: {tp}"
        )
        send_telegram_alert(msg)
        was_sent = "yes"

    # 4. Loga o sinal no Supabase
    log_signal(
        signal=trade_signal,
        sl=sl,
        tp=tp,
        trend=trend_signal,
        sentiment=sentiment_signal,
        entry_price=entry_price,
        sent=was_sent,
        future_high=future_high,
        future_low=future_low,
    )

    print("✅ run_signal executado com sucesso.")

except Exception as e:
    print(f"❌ Erro ao executar run_signal: {e}")
