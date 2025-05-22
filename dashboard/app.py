import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from signals import engine

st.set_page_config(page_title="EUR/USD AI Dashboard", layout="wide")
st.title("📊 EUR/USD Trading Intelligence Dashboard")

try:
    # Run signal engine
    result = engine.run_signal_engine()

    if result['trend'] and result['sentiment']:
        st.success("✅ Data fetched successfully")

        # Display breakdown
        st.subheader("🔍 Signal Breakdown")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 📉 Trend")
            st.write(result['trend'])

        with col2:
            st.markdown("### 🧠 Sentiment")
            st.write(result['sentiment'])

        with col3:
            st.markdown("### 📟 Final Signal")
            st.write(result['final'])

        # Plot
        st.subheader("📈 EUR/USD Close Price (Last 5 Days)")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=result['chart'].index, y=result['chart']['close'], mode='lines+markers'))
        fig.update_layout(margin=dict(l=10, r=10, t=30, b=20), height=400)
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("⚠️ Could not fetch signals properly.")

except Exception as e:
    st.error(f"❌ Failed to load dashboard: {str(e)}")