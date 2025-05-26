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
import os

# ============================
# ✅ Load .env (se local)
# ============================
load_dotenv()

# ============================
# 🚀 EXECUTA SINAL E ALERTA
# ============================
def run():
    try:
        data = fetch_eurusd_data()
        trend = get_trend_signal(data)
        sentiment= get_sentiment_signal(df)
        signal = generate_trade_signal(trend, sentiment)
        sl, tp = calculate_sl_tp(data)

        entry_price = data["close"].iloc[-1]
        future_high = data["high"].iloc[-1]
        future_low = data["low"].iloc[-1]

        was_sent = signal in ["BUY", "SELL"]

        # ✅ Salva no Supabase
        log_to_supabase(
            signal, sl, tp, trend, sentiment,
            entry_price, was_sent, future_high, future_low
        )

        # 📬 Alerta Telegram
        if was_sent:
            send_telegram_alert(signal, sl, tp)

        print(f"✅ [{signal}] executado com sucesso.")

    except Exception as e:
        print("❌ Erro ao executar run_signal:", str(e))


if __name__ == "__main__":
    run()
