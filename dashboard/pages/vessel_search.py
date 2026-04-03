"""Vessel search and tracking interface."""
import streamlit as st


def render():
    st.header("🔍 Vessel Search")
    mmsi = st.text_input("Enter MMSI or vessel name")
    # TODO: Query FastAPI /vessels endpoint
    # TODO: Display position on map + risk profile + sanctions status
