import streamlit as st


def render_metadata(
        data,
        unidades,
        show_metadata=True,
):
    """
    Exibe os parâmetros técnicos do fluido.
    """

    if not show_metadata or not data:
        return

    metadata = data.get("metadata", {})

    st.markdown("### Parâmetros do fluido")

    for k, v in metadata.items():
        unidade = unidades.get(k, "")
        st.write(f"**{k}**: {v} {unidade}")