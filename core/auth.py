import streamlit as st

def get_headers():

    token = st.session_state.get("token", "")

    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }