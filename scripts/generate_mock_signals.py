import csv
import os
from datetime import datetime, timedelta
import random

file = "db/signals_log.csv"

# Campos
fields = [
    "Timestamp", "Signal", "SL", "TP", "Trend", "Sentiment",
    "Price", "Hit", "Return (%)", "Capital", "Sent"
]

# Configurações
initial_capital = 10000
risk_percent = 1.0
num_signals = 20
capital = initial_capital
now = datetime.now()

# Geração
rows = []
for i in range(num_signals):
    timestamp = (now - timedelta(hours=num_signals - i)).strftime("%Y-%m-%d %H:%M:%S")
    signal = random.choice(["BUY", "SELL"])
    trend = "uptrend" if signal == "BUY" else "downtrend"
    sentiment = "bullish" if signal == "BUY" else "bearish"
    price = round(random.uniform(1.07, 1.10), 5)
    rr_ratio = random.uniform(0.8, 1.5)
    sl = round(price * 0.995, 5)
    tp = round(price * 1.005, 5)
    hit = random.choice(["TP", "SL"])
    retorno = risk_percent * rr_ratio if hit == "TP" else -risk_percent
    capital += capital * (retorno / 100)
    sent = "Yes"

    row = {
        "Timestamp": timestamp,
        "Signal": signal,
        "SL": sl,
        "TP": tp,
        "Trend": trend,
        "Sentiment": sentiment,
        "Price": price,
        "Hit": hit,
        "Return (%)": round(retorno, 2),
        "Capital": round(capital, 2),
        "Sent": sent
    }
    rows.append(row)

# Salva
os.makedirs("db", exist_ok=True)
with open(file, mode="w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ {num_signals} sinais mockados salvos em '{file}' com sucesso!")
