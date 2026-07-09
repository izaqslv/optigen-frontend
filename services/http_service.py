import requests
import streamlit as st

from core.auth import get_headers
def safe_request(url, params=None):
    headers = {}

    if "token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state.token}"

    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=(60, 60)
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro real: {e}")
        st.warning("Servidor temporariamente indisponível")
        return None