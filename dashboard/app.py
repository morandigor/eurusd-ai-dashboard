import streamlit as st
from signals import engine

st.set_page_config(page_title="EUR/USD AI Dashboard", layout="wide")

st.title("📊 EUR/USD Trading Intelligence Dashboard")

try:
    trend, sentiment, final_signal, df = engine.evaluate_and_alert()
    st.success("✅ Data fetched successfully")

    st.subheader("🔍 Signal Breakdown")
    col1, col2, col3 = st.columns(3)
    col1.markdown("📉 **Trend**")
    col1.markdown(f"**{trend}**")
    col2.markdown("🧠 **Sentiment**")
    col2.markdown(f"**{sentiment}**")
    col3.markdown("🚦 **Final Signal**")
    col3.markdown(f"**{final_signal}**")

    st.subheader("📈 EUR/USD Close Price (Last 5 Days)")
    st.line_chart(df.set_index("datetime")["close"].tail(5))

except Exception as e:
    st.error(f"❌ Failed to load dashboard: {e}")
