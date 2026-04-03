"""PyGWalker interactive EDA explorer."""
import streamlit as st


def render():
    st.header("📊 Data Explorer")
    st.info("Interactive Tableau-like exploration of maritime data via PyGWalker.")
    # TODO: Load sample Gold data from Snowflake
    # TODO: pyg.walk(df, env="Streamlit")
