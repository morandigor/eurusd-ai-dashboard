# 📈 EUR/USD AI Trading Dashboard

An AI-powered trading assistant built with **Streamlit**, using real-time **EUR/USD price data** from Twelve Data API and auto-alerts via **Telegram**. Designed to help traders receive clean, automated, and trackable trade signals.

---

## 🚀 Features

- ✅ Real-time EUR/USD data from Twelve Data API  
- ✅ AI-generated signals based on trend + sentiment  
- ✅ Automatic Stop Loss and Take Profit levels  
- ✅ Telegram alerts sent for every BUY/SELL signal  
- ✅ Signal logging to `signals_log.csv`  
- ✅ Dashboard auto-refresh every 15 minutes  
- ✅ Interactive performance tracking and stats

---

## 🧠 How It Works

1. Fetches EUR/USD data (1-hour candles) from Twelve Data.
2. Calculates trend via moving averages.
3. Injects static sentiment (extendable to NLP).
4. Generates signals: `BUY`, `SELL`, or `WAIT`.
5. Sends alert via Telegram for actionable signals.
6. Logs all signals into CSV for backtesting and performance evaluation.

---

## 📊 Example Screenshot

![dashboard](https://your-screenshot-url.png)

---

## 🛠 Project Structure

eurusd-ai-dashboard/
├── app/
│ ├── engine.py # Core logic: data, signals, logging
│ ├── telegram.py # Telegram alert integration
├── app.py # Streamlit UI + logic
├── signals_log.csv # Logged signals (auto-created)
├── logs.txt # Raw logs (optional)
└── requirements.txt # Python dependencies


---

## 🔐 Secrets Configuration

This project uses `st.secrets` (for Streamlit Cloud) or a `.env` file locally.

### Local `.env` (for development):
TWELVE_DATA_API_KEY=your_twelve_data_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

📦 Installation
git clone https://github.com/seu-usuario/eurusd-ai-dashboard.git
cd eurusd-ai-dashboard
pip install -r requirements.txt
streamlit run app.py

🧠 Future Plans
 Add backtest module

 Email alert option

 NLP-based sentiment from news feed

 Tiered monetization (Freemium / Pro)

👨‍💻 Built by
MrDin

International Marketing + Tech + Trading | @yourhandle