"""Agentic chat interface."""
import streamlit as st


def render():
    st.header("💬 Maritime Risk Chat")
    st.markdown("Ask questions about maritime risk, vessel status, or route advisories.")
    # TODO: Chat interface posting to FastAPI /chat endpoint
    # TODO: Display agent responses with citations
    # TODO: HITL approval widget for high-risk advisories
