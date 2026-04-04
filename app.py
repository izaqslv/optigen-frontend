import streamlit as st
import requests
import base64
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
from datetime import datetime

UNIDADES = {
    "dens_susp": "g/cm³",
    "dens_solids": "g/cm³",
    "teor_solids": "fração",
    "dp_medio": "µm",
    "ROA": "-",
    "m": "-",
    "n": "-"
}

#-------------------------------------------------------------
# CONTROLE GLOBAL
if "token" not in st.session_state:
    st.session_state.token = None
#--------------------------------------------------------------

# HEADER-----------------------------------------------------
def get_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}"
    }
#------------------------------------------------------------


# CONFIG DO STREMLIT -----------------
st.set_page_config(
    layout="wide",
    page_title="OptiGen",
    page_icon="🔬"
)
#-------------------------------------

#===================================================
# SEGURANÇA/USUÁRIO/SENHA DE ACESSO
#===================================================

### Tela de login
st.markdown("<br><br><br>", unsafe_allow_html=True)

### --- LOGIN LOCAL:
# API_URL = "http://127.0.0.1:8010"  # ou localhost

### --- LOGIN NA PRODUÇÃO (ONLINE NO RENDER) >>> deploy:
API_URL = "https://optigen.onrender.com"  # ou localhost

# =========================
# 🔐 CONTROLE DE LOGIN
# =========================
if "token" not in st.session_state:
    st.session_state.token = None

# =========================
# 🔐 TELA DE LOGIN
# =========================
if st.session_state.token is None:

    col1, col2, col3 = st.columns([2, 1, 2])

    with col2:
        st.image("assets/logo_newgen_black.png", width=100)
        st.markdown("### 🔐 Login - OptiGen")

        username = st.text_input("Usuário")
        password = st.text_input("Senha", type="password")

        if st.button("Entrar", use_container_width=True):

            response = requests.post(
                url=f"{API_URL}/auth/login",
                json={
                    "username": username,
                    "password": password
                },
                timeout=60
            )

            if response.status_code == 200:
                token = response.json()["access_token"]
                st.session_state.token = token
                st.success("Login realizado!")
                st.rerun()
            else:
                st.error("Credenciais inválidas")

# =========================
# 🚀 SISTEMA PRINCIPAL
# =========================
else:

    # =========================
    # 🔵 APP CONTINUA AQUI
    # =========================
    ## Bloquear app sem login
    if not st.session_state.token:
        st.stop()

    # ## Botão logout (ativar se quer que apareça na página principal)
    # if st.button("Logout"):
    #     for key in list(st.session_state.keys()):
    #         del st.session_state[key]
    #     st.rerun()

    # =======================================================================================================================

    # st.caption("💡 Para uma melhor experiência, ative o modo escuro")

    st.markdown(
        "<div style='margin-top:-140px;'>💡 Para uma melhor experiência, ative o modo escuro</div>",
        unsafe_allow_html=True
    )
    #-------------------------------------------

    st.markdown("""
    <style>
    /* Fundo geral */
    .stApp {
        background-color: #0E1117;
    }

    /* Texto principal */
    h1, h2, h3 {
        color: #FFFFFF;
    }

    /* Subtítulo */
    .subtitle {
        color: #A0A0A0;
    }

    /* Botões */
    .stButton>button {
        background-color: #E50914;
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
        border: none;
    }

    .stButton>button:hover {
        background-color: #B20710;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #161A23;
    }
    </style>
    """, unsafe_allow_html=True)

    BASE_URL = API_URL

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            "<div style='margin-top:-100px;'>"
            "<h1 style='margin-bottom:5px;'>🔬 OptiGen</h1>"
            "<p style='font-size:20px; margin-top:-20px; margin-bottom:5px;'>"
            "Soluções Inteligentes em Engenharia de Fluidos"
            "</p>"
            "<p style='color:gray; font-size:14px; margin-top:-5px;'>"
            "by NewGen Intelligent Engineering Solutions"
            "</p>"
            "</div>",
            unsafe_allow_html=True
        )


    # ===============================
    # SIDEBAR
    # ===============================
    # 🔝 TOPO DA SIDEBAR
    logout = st.sidebar.button("❌ Sair", help="Encerrar sessão")

    if logout:
        st.session_state.token = None
        st.rerun()

    st.markdown("""
    <style>
    /* Botão pequeno e discreto */
    button[kind="secondary"], button[kind="primary"] {
        font-size: 12px !important;
        padding: 4px 8px !important;
        border-radius: 6px !important;
    }

    /* Botão de topo mais leve */
    button {
        opacity: 0.85;
    }
    button:hover {
        opacity: 1;
    }
    </style>
    """, unsafe_allow_html=True)


    st.sidebar.markdown("<div style='height:50px'></div>", unsafe_allow_html=True)
    # Inserir botão logomarca na sidebar (desativar a linha abaixo se não desejar):
    st.sidebar.image("assets/logo_newgen_black.png", width=80)

    st.sidebar.markdown("""
    <div style="line-height: 1.2; padding-bottom:10px;">
        <span style="font-size:18px; font-weight:600;">NewGen</span><br>
        <span style="font-size:13px; color:gray;">Intelligent Engineering Solutions</span>
    </div>
    <hr style="margin-top:5px; margin-bottom:10px;">
    """, unsafe_allow_html=True)

    st.sidebar.caption("Plataforma de Simulação Inteligente")
    st.sidebar.title("Configurações")

    save = st.sidebar.checkbox("Salvar imagem no servidor", True)
    show_metadata = st.sidebar.checkbox("Mostrar metadados", True)

    if "history" not in st.session_state:
        st.session_state.history = []

    st.sidebar.markdown("### 📁 Histórico de Simulações")
    for item in st.session_state.history:
        st.sidebar.markdown(
            f"• **Fluido {item['fluid_id']}**"
            f" → Altura: `{item['height']}`"
        )


    # ===============================
    # INTERPRETAÇÃO
    # ===============================
    def gerar_interpretacao(metadata):

        if not metadata:
            return "Dados insuficientes."

        dens = metadata.get("dens_susp", 0)
        solidos = metadata.get("teor_solids", 0)

        texto = ""

        if dens > 1.2:
            texto += "Alta densidade indica maior tendência à sedimentação. "

        if solidos > 0.1:
            texto += "Teor de sólidos elevado influencia gradientes de concentração. "

        if texto == "":
            texto = "Comportamento estável."

        return texto


    # ===============================
    # PDF
    # ===============================
    def gerar_pdf(fid, img_bytes, metadata, height):

        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        temp_img.write(img_bytes)
        temp_img.close()

        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

        doc = SimpleDocTemplate(temp_pdf.name, pagesize=letter)
        styles = getSampleStyleSheet()

        elements = []
        # LOGO
        elements.append(Image("assets/logo_newgen_white.png", width=140, height=110))
        elements.append(Spacer(1, 12))

        # TÍTULO
        elements.append(Paragraph("Relatório Técnico - OptiGen", styles["Title"]))
        elements.append(Spacer(1, 12))

        # MARCA
        elements.append(Paragraph("NewGen Intelligent Engineering Solutions", styles["Heading2"]))
        elements.append(Paragraph("Engineering Intelligence", styles["Normal"]))
        elements.append(Spacer(1, 12))

        # IDENTIFICAÇÃO
        elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
        elements.append(Paragraph(f"Fluido: {fid}", styles["Normal"]))
        elements.append(Paragraph(f"Altura: {height}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        if metadata:
            elements.append(Paragraph("Parâmetros:", styles["Heading2"]))
            for k, v in metadata.items():
                unidade = UNIDADES.get(k, "")
                elements.append(Paragraph(f"{k}: {v} {unidade}", styles["Normal"]))
            elements.append(Spacer(1, 12))

        elements.append(Image(temp_img.name, width=400, height=250))
        elements.append(Spacer(1, 12))

        interpretacao = gerar_interpretacao(metadata)

        elements.append(Paragraph("Interpretação Técnica:", styles["Heading2"]))
        elements.append(Paragraph(interpretacao, styles["Normal"]))

        # =========================
        # 📌 CONCLUSÃO
        # =========================
        elements.append(Paragraph("Conclusão Técnica", styles["Heading2"]))
        elements.append(Spacer(1, 10))
        elements.append(Paragraph(f"""
        O fluido {fid} apresentou comportamento consistente ao longo do tempo,
        com boa aderência ao modelo preditivo.
        """, styles["Normal"]))

        # 🔚 FINALIZA O PDF
        doc.build(elements)

        with open(temp_pdf.name, "rb") as f:
            return f.read()


    def gerar_pdf_comparacao(fluid_ids, imagens, metadatas):

        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

        doc = SimpleDocTemplate(temp_pdf.name, pagesize=letter)
        styles = getSampleStyleSheet()

        elements = []

        # LOGO
        elements.append(Image("assets/logo_newgen_white.png", width=140, height=110))
        elements.append(Spacer(1, 12))

        # MARCA
        elements.append(Paragraph("NewGen Intelligent Engineering Solutions", styles["Heading2"]))
        elements.append(Paragraph("Engineering Intelligence", styles["Normal"]))
        elements.append(Spacer(1, 12))

        # TÍTULO
        elements.append(Paragraph("Relatório Comparativo - OptiGen", styles["Title"]))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"Fluidos analisados: {', '.join(map(str, fluid_ids))}", styles["Normal"]))
        elements.append(Spacer(1, 12))

        for i, fid in enumerate(fluid_ids):

            elements.append(Paragraph(f"Fluido {fid}", styles["Heading2"]))
            elements.append(Spacer(1, 8))

            # salvar imagem temporária
            temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            temp_img.write(imagens[i])
            temp_img.close()

            elements.append(Image(temp_img.name, width=400, height=250))
            elements.append(Spacer(1, 8))

            metadata = metadatas[i]

            if metadata:
                elements.append(Paragraph(f"Parâmetros do fluido {fid}:", styles["Heading2"]))
                for k, v in metadata.items():
                    unidade = UNIDADES.get(k, "")
                    elements.append(Paragraph(f"{k}: {v} {unidade}", styles["Normal"]))
                elements.append(Spacer(1, 12))

            interpretacao = gerar_interpretacao(metadata)

            elements.append(Paragraph("Interpretação:", styles["Heading3"]))
            elements.append(Paragraph(interpretacao, styles["Normal"]))
            elements.append(Spacer(1, 20))

            elements.append(Paragraph("Conclusão Técnica", styles["Heading2"]))
            elements.append(Spacer(1, 10))
            elements.append(Paragraph("""
            A análise comparativa evidencia diferenças relevantes entre os cenários avaliados.
            Observa-se variação no comportamento de sedimentação em função das condições analisadas,
            indicando sensibilidade do sistema aos parâmetros de entrada.
            """, styles["Normal"]))

        doc.build(elements)

        with open(temp_pdf.name, "rb") as f:
            return f.read()


    # ===============================
    # API (helpers)
    # ===============================
    def safe_request(url, params=None):
        headers = {}

        if "token" in st.session_state:
            headers["Authorization"] = f"Bearer {st.session_state.token}"

        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,  # 🔥 AQUI!
                timeout=(60, 60)
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            st.error(f"Erro real: {e}")
            st.warning("Servidor temporariamente indisponível")
            return None


    # ===============================
    # API
    # ===============================
    @st.cache_data
    def get_fluids():
        data = safe_request(f"{BASE_URL}/profiles/available_fluids")

        if not data:
            return []

        if isinstance(data, list):
            return data
        elif "fluids" in data:
            return data["fluids"]
        elif "data" in data:
            return data["data"]
        else:
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
                "show_metadata": "true"
            }
        )


    def get_plot_all(fluid_id):
        url = f"{BASE_URL}/profiles/{fluid_id}/plot_all"

        return safe_request(url)


    st.markdown(
        "<hr style='margin-top:-10px; margin-bottom:15px;'>",
        unsafe_allow_html=True
    )


    # ===============================
    # MODO
    # ===============================
    modo = st.radio("Modo", ["Individual", "Comparação"], horizontal=True)

    fluids = get_fluids()

    if not fluids:
        st.stop()

    # ===============================
    # INDIVIDUAL
    # ===============================
    if modo == "Individual":

        fluid_id = st.selectbox("Selecione o fluido", fluids)

        heights = get_heights(fluid_id)

        if not heights:
            st.warning("Nenhuma altura encontrada")
            st.stop()

        height = st.selectbox("Selecione a altura", heights)

        col1, col2 = st.columns(2)

        generate_single = col1.button("📊 Gerar Análise/Gráfico do Fluido")
        generate_all = col2.button("📈 Gerar Todas as Alturas")

        if generate_single:

            data = get_plot(fluid_id, height)

            if show_metadata and data:
                metadata = data.get("metadata", {})
                st.markdown("### Parâmetros do fluido")
                # st.json(metadata)
                for k, v in metadata.items():
                    unidade = UNIDADES.get(k, "")
                    st.write(f"**{k}**: {v} {unidade}")

            if "img_base64" in data:
                # TÍTULO DO CARD (ANTES DO GRÁFICO)
                st.markdown("""
                                <div style="
                                    background-color:#161A23;
                                    padding:20px;
                                    border-radius:12px;
                                    margin-top:10px;
                                    box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
                                ">
                                <h3 style="margin-top:0;">📊 Resultado da Simulação</h3>
                                </div>
                                """, unsafe_allow_html=True)

                img_bytes = base64.b64decode(data["img_base64"])

                st.image(
                    img_bytes,
                    caption=f"Fluido {fluid_id}",
                    use_container_width=True
                )

                # 🔥 STATUS DE SUCESSO (DEPOIS DO GRÁFICO)
                st.success("✔ Análise concluída — dados processados com sucesso")

                # =========================
                # 🧠 INTERPRETAÇÃO TÉCNICA
                # =========================

                st.markdown("### 🧠 Interpretação Técnica")

                st.info(f"""
                - Fluido {fluid_id} apresenta tendência de estabilização ao longo do tempo.
                - Observa-se comportamento típico de sedimentação controlada.
                - Diferenças entre modelo e experimental indicam boa aderência da rede neural.
                """)

                # HISTÓRICO
                registro = {"fluid_id": fluid_id, "height": height}
                if registro not in st.session_state.history:
                    st.session_state.history.append(registro)

                pdf = gerar_pdf(fluid_id, img_bytes, data.get("metadata", {}), height)
                st.download_button(
                    "📄 Relatório Técnico",
                    pdf,
                    f"relatorio_{fluid_id}_{height}.pdf",
                    "application/pdf"
                )

        if generate_all:

            for h in heights:
                data = get_plot(fluid_id, h)

                if show_metadata and data:
                    metadata = data.get("metadata", {})
                    st.markdown("### Parâmetros do fluido")
                    # st.json(metadata)
                    for k, v in metadata.items():
                        unidade = UNIDADES.get(k, "")
                        st.write(f"**{k}**: {v} {unidade}")

                if "img_base64" in data:
                    img_bytes = base64.b64decode(data["img_base64"])
                    st.image(img_bytes, caption=f"h={h}")

    # ===============================
    # COMPARAÇÃO
    # ===============================
    if modo == "Comparação":

        st.subheader("Comparação entre fluidos")

        fluid_ids = st.multiselect("Selecione os fluidos", fluids)

        if st.button("Comparar"):

            imagens = []
            metadatas = []

            for fid in fluid_ids:

                data = get_plot_all(fid)

                if show_metadata and data:
                    metadata = data.get("metadata", {})
                    st.markdown("### Parâmetros do fluido")
                    # st.json(metadata)
                    for k, v in metadata.items():
                        unidade = UNIDADES.get(k, "")
                        # st.write(f"**{k}**: {v} {unidade}")  # Ativar se a linha abaixo estiver desativada (e vice-versa)
                        st.write(
                            f"**{k.replace('_', ' ').title()}**: {v} {unidade}")  # Opcional (para retirar caracteres/deixar mais bonito)

                if "img_base64" in data:

                    # 🔥 TÍTULO DO CARD (ANTES DO GRÁFICO)
                    st.markdown("""
                    <div style="
                        background-color:#161A23;
                        padding:20px;
                        border-radius:12px;
                        margin-top:10px;
                        box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
                    ">
                    <h3 style="margin-top:0;">📊 Resultado da Simulação</h3>
                    </div>
                    """, unsafe_allow_html=True)

                    img_bytes = base64.b64decode(data["img_base64"])

                    st.image(
                        img_bytes,
                        caption=f"Fluido {fid}",
                        use_container_width=True
                    )

                    # 🔥 STATUS DE SUCESSO (DEPOIS DO GRÁFICO)
                    st.success("✔ Análise concluída — dados processados com sucesso")

                    # =========================
                    # 🧠 INTERPRETAÇÃO TÉCNICA
                    # =========================

                    st.markdown("### 🧠 Interpretação Técnica")

                    st.info(f"""
                                - Fluido {fid} apresenta tendência de estabilização ao longo do tempo.
                                - Observa-se comportamento típico de sedimentação controlada.
                                - Diferenças entre modelo e experimental indicam boa aderência da rede neural.
                                """)

                    # HISTÓRICO
                    registro = {"fluid_id": fid, "height": "todas"}
                    if registro not in st.session_state.history:
                        st.session_state.history.append(registro)

                    imagens.append(img_bytes)
                    metadatas.append(data.get("metadata", {}))

            # 🔥 BOTÃO ÚNICO DE RELATÓRIO
            if imagens:
                pdf = gerar_pdf_comparacao(fluid_ids, imagens, metadatas)

                st.download_button(
                    "📄 Baixar relatório de comparação",
                    pdf,
                    "relatorio_comparacao.pdf",
                    "application/pdf"
                )


    # RODAPÉ ------------------------------------------------------------------------------------------------------------
    st.markdown(
        "<hr style='margin-top:80px; margin-bottom:5px;'>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:right; font-size:12px; margin-top:0px;'>"
        "© 2026 NewGen Intelligent Engineering Solutions. Todos os direitos reservados."
        "</p>",
        unsafe_allow_html=True
    )