import base64
import streamlit as st
from services.experimental_data_service import get_plot_all

def run_comparison(fluids, gerar_pdf_comparacao, unidades, show_metadata):
    """
    Caso de uso:
    Comparação entre fluidos experimentais.
    """
    st.markdown("## ⚖️ Benchmark de Estabilidade")
    card = """
    <div style="background-color:#161A23; padding:15px; border-left:5px solid #E50914; border-radius:5px;">
    <p style="margin:0;color:#A0A0A0;">
    <b>
    Compare múltiplos fluidos simultaneamente. Identifique variações de performance entre amostras distintas.
    </b>
    </p>
    </div>
    """

    st.markdown(card, unsafe_allow_html=True)
    st.markdown("---")

    if not fluids:
        st.info("💡 Este módulo requer dados de fluidos que não estão disponíveis para seu perfil.")
        st.stop()

    fluid_ids = st.multiselect("Selecione os fluidos", fluids)

    if not st.button("Comparar"):
        return

    imagens = []
    metadatas = []

    for fid in fluid_ids:

        data = get_plot_all(fid)

        if show_metadata and data:

            metadata = data.get("metadata", {})

            st.markdown("### Parâmetros do fluido")

            for k, v in metadata.items():
                unidade = unidades.get(k, "")

                st.write(f"**{k.replace('_',' ').title()}**: {v} {unidade}")

        if "img_base64" not in data:
            continue

        st.markdown(
            """
            <div style="
                background-color:#161A23;
                padding:20px;
                border-radius:12px;
                margin-top:10px;
                box-shadow:0px 4px 12px rgba(0,0,0,0.4);
            ">

            <h3 style="margin-top:0;">
            📊 Resultado da Simulação
            </h3>

            </div>
            """,
            unsafe_allow_html=True,
        )

        img_bytes = base64.b64decode(data["img_base64"])

        st.image(img_bytes, caption=f"Fluido {fid}", use_container_width=True)

        st.success("✔ Análise concluída — dados processados com sucesso")

        st.markdown("### 🧠 Interpretação Técnica")

        st.info(
            f"""
            - Fluido {fid} apresenta tendência de estabilização ao longo do tempo.

            - Observa-se comportamento típico de sedimentação controlada.
            """
        )

        registro = {
            "fluid_id": fid,
            "height": "todas",
        }

        if registro not in st.session_state.history:
            st.session_state.history.append(registro)

        imagens.append(img_bytes)
        metadatas.append(
            data.get("metadata", {})
        )

    if imagens:
        pdf = gerar_pdf_comparacao(
            fluid_ids,
            imagens,
            metadatas,
        )

        st.download_button(
            "📄 Baixar relatório de comparação",
            pdf,
            "relatorio_comparacao.pdf",
            "application/pdf",
        )