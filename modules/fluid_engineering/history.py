import streamlit as st


def update_history(fluid_id, height):
    """
    Atualiza o histórico da sessão.
    """

    registro = {
        "fluid_id": fluid_id,
        "height": height,
    }

    if registro not in st.session_state.history:
        st.session_state.history.append(registro)