"""Real-time alert feed."""
import streamlit as st


def render():
    st.header("🚨 Active Alerts")
    # TODO: Stream alerts from FastAPI /alerts endpoint
    # TODO: Display HITL approval panel for risk > 75
