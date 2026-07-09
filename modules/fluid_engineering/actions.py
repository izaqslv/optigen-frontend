import streamlit as st

def render_actions():

    col1, col2 = st.columns(2)

    generate_single = col1.button(
        "📊 Gerar Análise/Gráfico do Fluido"
    )

    generate_all = col2.button(
        "📈 Gerar Todas as Alturas"
    )

    return generate_single, generate_all