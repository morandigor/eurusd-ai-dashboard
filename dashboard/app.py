import streamlit as st
import pandas as pd
import engine

st.set_page_config(page_title="EUR/USD AI Dashboard", layout="wide")
st.title("📊 EUR/USD Trading Intelligence Dashboard")

try:
    df = engine.fetch_eurusd_data()
    st.success("✅ Data fetched successfully")

    trend = engine.get_trend_signal(df)
    sentiment = engine.get_sentiment_signal(df)
    final_signal = engine.generate_trade_signal(trend, sentiment)

    # Optionally define SL/TP (example: recent high/low)
    sl = round(df["close"].iloc[-1] - 0.0010, 5)
    tp = round(df["close"].iloc[-1] + 0.0020, 5)

    # Send alert
    engine.send_telegram_alert(final_signal, sl=sl, tp=tp)

    # === Layout ===
    st.header("🔍 Signal Breakdown")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("📉 **Trend**")
        st.subheader(trend)
    with col2:
        st.markdown("🧠 **Sentiment**")
        st.subheader(sentiment)
    with col3:
        st.markdown("🚦 **Final Signal**")
        st.subheader(final_signal)

    # === Chart ===
    st.subheader("📈 EUR/USD Close Price (Last 5 Days)")
    recent = df[df["datetime"] > pd.Timestamp.now() - pd.Timedelta(days=5)]
    st.line_chart(recent.set_index("datetime")["close"])

except Exception as e:
    st.error(f"❌ Failed to load dashboard: {str(e)}")
