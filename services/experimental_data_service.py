import requests
import streamlit as st
from core.config import BASE_URL
from services.http_service import safe_request


@st.cache_data(ttl=600)
def get_fluids(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        response = requests.get(
            f"{BASE_URL}/profiles/available_fluids",
            headers=headers,
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("fluids", [])

        return []

    except Exception:
        return []

@st.cache_data
def get_heights(fluid_id):
    data = safe_request(
        f"{BASE_URL}/profiles/available_heights",
        params={"fluid_id": fluid_id}
    )

    if not data:
        return []

    if isinstance(data, list):
        return data
    elif "heights_cm" in data:
        return data["heights_cm"]
    elif "data" in data:
        return data["data"].get("heights_cm", [])
    else:
        return []


def get_plot(fluid_id, height):
    url = f"{BASE_URL}/profiles/{fluid_id}/height/plot"

    return safe_request(
        url,
        params={
            "height": height,
            "save": "false",
            "SHOW_METADATA": "true"
        }
    )


def get_plot_all(fluid_id):
    url = f"{BASE_URL}/profiles/{fluid_id}/plot_all"

    return safe_request(url)


# st.markdown(
#     "<hr style='margin-top:-10px; margin-bottom:15px;'>",
#     unsafe_allow_html=True
# )