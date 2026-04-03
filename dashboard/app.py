"""Streamlit entry point — Maritime AI Sentinel Dashboard."""
import streamlit as st

st.set_page_config(
    page_title="Maritime AI Sentinel",
    page_icon="🚢",
    layout="wide",
)

st.title("🚢 Maritime AI Sentinel")
st.markdown("Global Maritime Supply Chain Resilience via Geopolitical Event Tracking and Agentic AI")

# Sidebar navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Globe View", "Risk Heatmap", "Vessel Search", "Alerts", "EDA Explorer", "Chat"]
)

if page == "Globe View":
    from dashboard.pages import globe
    globe.render()
elif page == "Risk Heatmap":
    from dashboard.pages import risk_heatmap
    risk_heatmap.render()
elif page == "Vessel Search":
    from dashboard.pages import vessel_search
    vessel_search.render()
elif page == "Alerts":
    from dashboard.pages import alerts
    alerts.render()
elif page == "EDA Explorer":
    from dashboard.pages import eda
    eda.render()
elif page == "Chat":
    from dashboard.pages import chat
    chat.render()
