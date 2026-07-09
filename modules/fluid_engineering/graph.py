import base64
import streamlit as st


def render_graph(data):
    """
    Renderiza o gráfico retornado pela API.
    """

    if "img_base64" not in data:
        return None

    st.markdown("""
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
    """, unsafe_allow_html=True)

    img_bytes = base64.b64decode(data["img_base64"])

    st.image(
        img_bytes,
        caption=f"Fluido {data.get('fluid_id', '')}",
        use_container_width=True
    )

    st.success("✔ Análise concluída — dados processados com sucesso")

    return img_bytes