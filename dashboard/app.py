import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from signals import engine

st.set_page_config(page_title="EUR/USD Trading Intelligence Dashboard")
st.title("\ud83d\udcca EUR/USD Trading Intelligence Dashboard")

try:
    df = engine.fetch_data()
    st.success("\u2705 Data fetched successfully")

    trend = engine.get_trend_signal(df)
    sentiment = engine.get_sentiment_signal(df)
    final_signal = engine.generate_trade_signal(trend, sentiment)

    # SL and TP logic
    entry_price = df["close"].iloc[-1]
    sl = round(entry_price * 0.995, 5)
    tp = round(entry_price * 1.005, 5)

    engine.send_telegram_alert(final_signal, entry_price, sl, tp)

    st.subheader("\ud83d\udd0d Signal Breakdown")
    col1, col2, col3 = st.columns(3)
    col1.metric("\ud83d\udece\ufe0f Trend", trend)
    col2.metric("\ud83d\udc8e Sentiment", sentiment)
    col3.metric("\ud83d\udd39 Final Signal", final_signal)

    st.subheader("\ud83d\udd3c EUR/USD Close Price (Last 5 Days)")
    st.line_chart(df.set_index("datetime")["close"])

except Exception as e:
    st.error(f"\u274c Failed to load dashboard: {e}")