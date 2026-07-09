from services.experimental_data_service import get_plot

import base64
import streamlit as st

from modules.fluid_engineering.metadata import render_metadata
from modules.fluid_engineering.graph import render_graph
from modules.fluid_engineering.interpretation import render_interpretation
from modules.fluid_engineering.history import update_history


def get_analysis_data(fluid_id, height):
    """
    Obtém os dados da análise individual.
    """
    return get_plot(fluid_id, height)


def execute_single_analysis(fluid_id, height):
    """
    Executa a análise individual.
    """
    return get_analysis_data(fluid_id, height)


def run_single_analysis(
        fluid_id,
        height,
        gerar_pdf,
        unidades,
        show_metadata,
):
    """
    Caso de uso:
    Executa uma análise individual completa.
    """

    data = execute_single_analysis(fluid_id, height)

    render_metadata(
        data=data,
        unidades=unidades,
        show_metadata=show_metadata,
    )

    if "img_base64" not in data:
        return

    img_bytes = render_graph(data)

    render_interpretation(
        fluid_id=fluid_id,
        data=data,
    )

    update_history(
        fluid_id=fluid_id,
        height=height,
    )

    pdf = gerar_pdf(
        fluid_id,
        img_bytes,
        data.get("metadata", {}),
        height,
    )

    st.download_button(
        label="📄 Relatório Técnico",
        data=pdf,
        file_name=f"relatorio_{fluid_id}_{height}.pdf",
        mime="application/pdf",
    )


def run_all_analysis(
        fluid_id,
        heights,
        unidades,
        show_metadata,
):
    """
    Caso de uso:
    Executa a análise para todas as alturas.
    """

    for h in heights:

        data = get_plot(fluid_id, h)

        render_metadata(
            data=data,
            unidades=unidades,
            show_metadata=show_metadata,
        )

        if "img_base64" in data:
            img_bytes = base64.b64decode(data["img_base64"])

            st.image(
                img_bytes,
                caption=f"h={h}",
            )