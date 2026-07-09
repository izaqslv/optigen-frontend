import streamlit as st
from services.experimental_data_service import get_heights
from .actions import render_actions

def render_experimental_data(fluids):
    """
    Caso de uso:
    Engenharia de Fluidos (Dados Experimentais)
    """
    render_header()
    fluid_id, heights, height = render_inputs(fluids)
    generate_single, generate_all = render_actions()
    return fluid_id, heights, height, generate_single, generate_all

def render_inputs(fluids):
    """
    Renderiza os parâmetros de entrada da análise.

    Returns
    -------
    tuple
        (fluid_id, height)
    """

    # ---------------------------------------
    if not fluids:
        st.info(
            "💡 Selecione um módulo no menu lateral ou aguarde o carregamento dos dados."
        )
        st.stop()
    # ---------------------------------------

    fluid_id = st.selectbox(
        "Selecione o fluido",
        fluids
    )

    heights = get_heights(fluid_id)

    if not heights:
        st.warning("Nenhuma altura encontrada")
        st.stop()

    height = st.selectbox(
        "Selecione a altura",
        heights
    )

    return fluid_id, heights, height


def render_header():
    st.markdown("## 📊 Análise de Perfil Estático")

    st.markdown(
        """
        <div style='background-color: #161A23;
                    padding:15px;
                    border-left:5px solid #E50914;
                    border-radius:5px;'>

        <p style='margin:0;color:#A0A0A0;'>

        <b>
        Exploração detalhada de perfis de sedimentação em fluidos
        de perfuração de poços de petróleo.
        Visualize curvas de concentração e metadados técnicos
        por altura.
        </b>

        </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")