import streamlit as st


def render_interpretation(
    fluid_id,
    data=None,
):
    """
    Exibe a interpretação técnica da análise.
    """

    st.markdown("### 🧠 Interpretação Técnica")

    st.info(f"""
- Fluido {fluid_id} apresenta tendência de estabilização ao longo do tempo.
- Observa-se comportamento típico de sedimentação controlada.
""")