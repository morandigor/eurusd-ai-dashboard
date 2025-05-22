import os
import sys
import streamlit as st
import plotly.graph_objects as go

# Ensure the project root is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
sys.path.append(ROOT_DIR)

from signals.engine import (
    generate_trade_signal,
    get_trend_signal,
    get_smart_money_signal,
    get_sentiment_signal,
)

st.set_page_config(page_title="EUR/USD Trading Intelligence", layout="wide")

st.markdown("## 💹 EUR/USD Trading Intelligence")

# Fetch signals
trend = get_trend_signal()
smart_money = get_smart_money_signal()
sentiment = get_sentiment_signal()
signal = generate_trade_signal(trend, smart_money, sentiment)

# Display signals
st.markdown("### 📊 Current Market Signals")
col1, col2, col3 = st.columns(3)
col1.metric("**Trend Signal**", trend)
col2.metric("**Smart Money**", smart_money)
col3.metric("**Sentiment**", sentiment)

st.markdown("### 🛑 Trade Signal")
st.success(f"**SIGNAL:** {signal}")

# Placeholder: live price chart (dummy data)
st.markdown("### 📈 EUR/USD Price Chart (Coming Soon)")
fig = go.Figure()
fig.update_layout(height=300, template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)
