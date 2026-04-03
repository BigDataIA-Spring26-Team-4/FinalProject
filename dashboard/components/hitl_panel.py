"""Human-in-the-Loop approval panel widget."""
import streamlit as st


def render_hitl_panel(alert: dict):
    """Render an approval/reject panel for a high-risk alert."""
    st.warning(f"⚠️ High-risk alert requires human review (score: {alert.get('risk_score', 'N/A')})")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✅ Approve", key=f"approve_{alert.get('id')}"):
            # TODO: POST approval to FastAPI
            st.success("Approved")
    with col2:
        if st.button("❌ Reject", key=f"reject_{alert.get('id')}"):
            st.error("Rejected")
    with col3:
        if st.button("✏️ Edit", key=f"edit_{alert.get('id')}"):
            st.text_area("Edit advisory", value=alert.get("advisory", ""))
