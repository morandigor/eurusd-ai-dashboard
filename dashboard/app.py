import streamlit as st
import pandas as pd
from datetime import datetime
import engine

st.set_page_config(page_title="EUR/USD AI Dashboard", layout="wide")
st.title("📊 EUR/USD Trading Intelligence Dashboard")

try:
    df = engine.fetch_eurusd_data()
    st.success("✅ Data fetched successfully")
except Exception as e:
    st.error(f"❌ Error fetching data: {e}")
    st.stop()

trend = engine.get_trend_signal(df)
sentiment = engine.get_sentiment_signal()
final_signal = engine.generate_trade_signal(trend, sentiment)

st.subheader("🔍 Signal Breakdown")
col1, col2, col3 = st.columns(3)
col1.markdown("🧭 **Trend**")
col1.markdown(f"**{trend}**")
col2.markdown("🧠 **Sentiment**")
col2.markdown(f"**{sentiment}**")
col3.markdown("📟 **Final Signal**")
col3.markdown(f"**{final_signal}**")

st.subheader("📉 EUR/USD Price (Last 5 Days)")
fig = pd.DataFrame({
    "Price": df["close"].values
}, index=df["datetime"])
st.line_chart(fig)

st.subheader("🎯 SL/TP Levels")
last_price = df["close"].iloc[-1]
stop_loss, take_profit = engine.calculate_sl_tp(last_price, final_signal)

col4, col5 = st.columns(2)
col4.metric("Stop Loss", stop_loss)
col5.metric("Take Profit", take_profit)

timestamp = datetime.utcnow().isoformat()
engine.log_signal(timestamp, final_signal, stop_loss, take_profit)

# Optional alert
if final_signal in ["BUY", "SELL"]:
    engine.send_telegram_alert(final_signal, stop_loss, take_profit)
