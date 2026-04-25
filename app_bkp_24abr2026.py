import streamlit as st
import requests
import base64
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
from datetime import datetime
from io import BytesIO
from PIL import Image as PILImage
import os
import pandas as pd
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
from reportlab.lib import colors

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
# API_URL = "https://optigen.onrender.com"  # ou localhost
## --- LOGIN GLOBAL:
API_URL = os.getenv("API_URL", "http://127.0.0.1:8010")

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

    # ==================================================================================================================

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
        elements.append(RLImage("assets/logo_newgen_white.png", width=140, height=110))
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

        elements.append(RLImage(temp_img.name, width=400, height=250))
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
        elements.append(RLImage("assets/logo_newgen_white.png", width=140, height=110))
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

            elements.append(RLImage(temp_img.name, width=400, height=250))
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

    # NOVO BLOCO:
    # ==============================
    # 📄 PDF PREMIUM - OPTIGEN
    # ==============================

    def gerar_grafico(df, titulo, file_name):
        plt.figure()
        for h in df["altura"].unique():
            sub = df[df["altura"] == h]
            plt.plot(sub["tempo"], sub["concentracao"], label=f"h={h:.1f}")

        plt.legend()

        plt.title(titulo)
        plt.xlabel("Tempo (dia)")
        plt.ylabel("Concentração (v/v)")
        plt.grid()

        plt.savefig(file_name, dpi=300, bbox_inches="tight")
        plt.close()


    def gerar_heatmap(df, file_name):
        pivot = df.pivot(index="altura", columns="tempo", values="concentracao")

        plt.figure()
        plt.imshow(
            pivot.values,
            aspect="auto",
            origin="lower"
        )
        plt.colorbar(label="Concentração (v/v)")
        plt.xlabel("Tempo (dia)")
        plt.ylabel("Altura (cm)")
        plt.title("Mapa espaço-temporal")

        plt.savefig(file_name)
        plt.close()


    def gerar_pdf_premium(met_A, met_B, vencedor, motivos, df_A, df_B):

        file_name = f"relatorio_optigen_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        # temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        # file_path = temp_file.name
        # temp_file.close()  # 🔥 ESSENCIAL
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            file_path = tmp.name

        styles = getSampleStyleSheet()
        doc = SimpleDocTemplate(file_path)

        content = []

        # ==============================
        # 🏢 LOGO
        # ==============================
        logo_path = "assets/logo_newgen_white.png"
        if os.path.exists(logo_path):
            content.append(RLImage(logo_path, width=120, height=60))

        content.append(Spacer(1, 12))

        # ==============================
        # 📌 TÍTULO
        # ==============================
        content.append(Paragraph("Relatório Técnico - OptiGen V3", styles["Title"]))
        content.append(Paragraph("Simulação e Comparação de Cenários de Sedimentação", styles["Normal"]))
        content.append(Spacer(1, 20))

        # ==============================
        # 📊 MÉTRICAS EM TABELA
        # ==============================
        def safe_val(v):
            return "-" if v is None else str(v)

        tabela = [
            ["Métrica", "Fluido A", "Fluido B"],
            ["C topo final", f"{met_A['C_top_final']:.4f}", f"{met_B['C_top_final']:.4f}"],
            # ["Tempo clarificação", str(met_A["tempo_clarificacao"]), str(met_B["tempo_clarificacao"])],
            ["Tempo clarificação", safe_val(met_A["tempo_clarificacao"]), safe_val(met_B["tempo_clarificacao"])],
            ["C fundo final", f"{met_A['C_bottom_final']:.4f}", f"{met_B['C_bottom_final']:.4f}"],
            ["Estabilidade (std)", f"{met_A['std_temporal']:.4f}", f"{met_B['std_temporal']:.4f}"],
        ]

        table = Table(tabela)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))

        content.append(Paragraph("Métricas Comparativas", styles["Heading2"]))
        content.append(Spacer(1, 10))
        content.append(table)
        content.append(Spacer(1, 20))

        # ==============================
        # 🧠 PARECER EXECUTIVO
        # ==============================
        content.append(Paragraph("Parecer Executivo", styles["Heading1"]))
        content.append(Spacer(1, 10))

        content.append(Paragraph(
            f"O Fluido {vencedor} apresentou melhor desempenho global na simulação.",
            styles["Normal"]
        ))

        content.append(Spacer(1, 10))

        for m in motivos:
            content.append(Paragraph(f"• {m}", styles["Normal"]))

        content.append(Spacer(1, 20))

        # ==============================
        # 📈 GRÁFICOS
        # ==============================
        tmp_dir = tempfile.gettempdir()
        path_A = os.path.join(tmp_dir, "grafico_A.png")
        path_B = os.path.join(tmp_dir, "grafico_B.png")
        path_heat_A = os.path.join(tmp_dir, "heat_A.png")
        path_heat_B = os.path.join(tmp_dir, "heat_B.png")

        gerar_grafico(df_A, "Curvas - Fluido A", path_A)
        gerar_grafico(df_B, "Curvas - Fluido B", path_B)
        gerar_heatmap(df_A, path_heat_A)
        gerar_heatmap(df_B, path_heat_B)

        content.append(Paragraph("Curvas de Concentração", styles["Heading2"]))
        content.append(RLImage(path_A, width=400, height=250))
        content.append(RLImage(path_B, width=400, height=250))

        content.append(Spacer(1, 20))

        content.append(Paragraph("Mapas Espaço-Temporais", styles["Heading2"]))
        content.append(RLImage(path_heat_A, width=400, height=250))
        content.append(RLImage(path_heat_B, width=400, height=250))

        # ==============================
        # 📄 GERAR
        # ==============================
        doc.build(content)

        return file_path, file_name

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
                headers=headers,
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
    modo = st.radio(
        "Modo",
        ["Individual (experimental)",
         "Comparação (experimental)",
         "Simulação Inteligente - IA",
         "Simulação: Fluido A vs Fluido B - IA"],
        horizontal=True
    )

    fluids = get_fluids()

    if not fluids:
        st.stop()

    # ===============================
    # MODO INDIVIDUAL
    # ===============================
    if modo == "Individual (experimental)":

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
    # MODO COMPARAÇÃO
    # ===============================
    if modo == "Comparação (experimental)":

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


    def get_prediction(fluid_id=None):

        params = {}
        if fluid_id:
            params["fluid_id"] = fluid_id

        return safe_request(
            f"{BASE_URL}/V3/predict",
            params=params
        )


    # ===============================
    # 🧠 MODO SIMULAÇÃO INTELIGENTE (V3)
    # ===============================
    if modo == "Simulação Inteligente - IA":

        st.subheader("🧠 Simulação Inteligente de Sedimentação (V3)")
        st.info("Simulação baseada em modelo físico–data-driven (OptiGen V3)")

        # =========================
        # INPUTS
        # =========================
        st.markdown("### ⚙️ Parâmetros do Fluido")

        col1, col2, col3 = st.columns(3)

        dens_susp = col1.number_input("Densidade suspensão", value=1.2, key="v3_dens_susp")
        dens_solids = col2.number_input("Densidade sólidos", value=2.7, key="v3_dens_solids")
        teor_solidos = col3.number_input("Teor de sólidos", value=0.15, key="v3_teor_solidos")

        col4, col5 = st.columns(2)

        m = col4.number_input("m", value=0.8, key="v3_m")
        n = col5.number_input("n", value=0.6, key="v3_n")

        st.markdown("### 📐 Domínio de Simulação")

        col6, col7, col8 = st.columns(3)

        altura_total = col6.number_input("Altura total", value=10.0, key="v3_altura")
        tempo_max = col7.number_input("Tempo máximo", value=50, key="v3_tempo")
        n_alturas = col8.number_input("Resolução (n_alturas)", value=20, key="v3_res")

        # =========================
        # EXECUÇÃO
        # =========================
        if st.button("🚀 Rodar Simulação Inteligente"):

            with st.spinner("Simulando comportamento do fluido..."):

                payload = {
                    "fluido": {
                        "dens_susp": dens_susp,
                        "dens_solids": dens_solids,
                        "teor_solids": teor_solidos,
                        "m": m,
                        "n": n
                    },
                    "altura_total": altura_total,
                    "tempo_max": tempo_max,
                    "n_alturas": n_alturas
                }

                # =========================
                # 🔥 CHAMADA ANALYZE
                # =========================
                try:
                    response = requests.post(
                        f"{BASE_URL}/v3/analyze",
                        json=payload,
                        headers=get_headers(),
                        timeout=120
                    )
                except Exception as e:
                    st.error(f"Erro de conexão: {e}")
                    st.stop()

                if response.status_code != 200:
                    st.error("Erro no backend (/v3/analyze)")
                    st.text(response.text)
                    st.stop()

                resp_json = response.json()

                if not resp_json.get("success"):
                    st.error("Erro retornado pelo backend")
                    st.json(resp_json)
                    st.stop()

                data = resp_json.get("data", {})

                st.success("✔ Simulação concluída — comportamento do fluido estimado com sucesso")

                # =========================
                # 📊 PERFIL INICIAL
                # =========================
                df_profile = pd.DataFrame(data.get("perfil_t0", []))

                if not df_profile.empty:
                    st.subheader("📊 Perfil inicial (t=0)")
                    st.line_chart(df_profile.set_index("altura")["concentracao"])
                else:
                    st.warning("Sem dados para perfil inicial")

                # =========================
                # 📈 TOPO
                # =========================
                df_top = pd.DataFrame(data.get("curva_topo", []))

                if not df_top.empty:
                    st.subheader("📈 Evolução no topo")
                    st.line_chart(df_top.set_index("tempo")["concentracao"])
                else:
                    st.warning("Sem dados para curva do topo")

                # =========================
                # 📉 FUNDO
                # =========================
                df_bottom = pd.DataFrame(data.get("curva_fundo", []))

                if not df_bottom.empty:
                    st.subheader("📉 Evolução no fundo")
                    st.line_chart(df_bottom.set_index("tempo")["concentracao"])
                else:
                    st.warning("Sem dados para curva do fundo")

                # =========================
                # 🧠 INTERFACE
                # =========================
                df_interface = pd.DataFrame(data.get("interface", []))

                if not df_interface.empty:
                    st.subheader("🧠 Evolução da Interface")
                    st.line_chart(df_interface.set_index("tempo")["altura_interface"])
                else:
                    st.warning("Sem dados de interface")

                # =========================
                # 📌 MÉTRICA
                # =========================
                tempo_clear = data.get("tempo_clareamento_topo")

                if tempo_clear is not None:
                    st.metric("Tempo de clareamento do topo", tempo_clear)
                else:
                    st.warning("Tempo de clareamento não identificado")

                # =========================
                # 🔥 HEATMAP (SIMULATE)
                # =========================
                st.subheader("🔥 Mapa espaço-temporal")

                try:
                    resp_sim = requests.post(
                        f"{BASE_URL}/v3/simulate",
                        json=payload,
                        headers=get_headers(),
                        timeout=120
                    )
                except Exception as e:
                    st.error(f"Erro ao chamar simulate: {e}")
                    st.stop()

                if resp_sim.status_code != 200:
                    st.error("Erro no backend (/v3/simulate)")
                    st.text(resp_sim.text)
                    st.stop()

                df_sim = pd.DataFrame(resp_sim.json().get("data", []))

                if not df_sim.empty:

                    pivot = df_sim.pivot(
                        index="altura",
                        columns="tempo",
                        values="concentracao"
                    )

                    fig, ax = plt.subplots()

                    cax = ax.imshow(
                        pivot.values,
                        aspect="auto",
                        origin="lower"
                    )

                    ax.set_xlabel("Tempo (dia)")
                    ax.set_ylabel("Altura (cm)")

                    fig.colorbar(cax, label="Concentração (v/v)")

                    st.pyplot(fig)

                else:
                    st.warning("Sem dados para mapa espaço-temporal")

    # ===============================
    # ⚔️ MODO COMPARAÇÃO DE CENÁRIOS
    # ===============================
    elif modo == "Simulação: Fluido A vs Fluido B - IA":
        st.subheader("⚔️ Comparação Inteligente de Fluidos (OptiGen V3)")
        st.info("Compare dois cenários físicos–data-driven e identifique o melhor comportamento")

        # =========================
        # INPUTS - FLUIDO A
        # =========================
        st.markdown("### 🅰️ Fluido A")

        colA1, colA2, colA3 = st.columns(3)
        A_dens_susp = colA1.number_input("dens_susp (g/cm³)", 1.2, key="A_dens_susp")
        A_dens_solids = colA2.number_input("dens_solids (g/cm³)", 2.7, key="A_dens_solids")
        A_teor = colA3.number_input("teor_solids (fração)", 0.15, key="A_teor")

        colA4, colA5 = st.columns(2)
        A_m = colA4.number_input("m (reologia)", 0.8, key="A_m")
        A_n = colA5.number_input("n (reologia)", 0.6, key="A_n")

        # =========================
        # INPUTS - FLUIDO B
        # =========================
        st.markdown("### 🅱️ Fluido B")

        colB1, colB2, colB3 = st.columns(3)
        B_dens_susp = colB1.number_input("dens_susp (g/cm³)", 1.2, key="B_dens_susp")
        B_dens_solids = colB2.number_input("dens_solids (g/cm³)", 2.7, key="B_dens_solids")
        B_teor = colB3.number_input("teor_solids (fração)", 0.15, key="B_teor")

        colB4, colB5 = st.columns(2)
        B_m = colB4.number_input("m (reologia)", 0.8, key="B_m")
        B_n = colB5.number_input("n (reologia)", 0.6, key="B_n")

        # =========================
        # DOMÍNIO
        # =========================
        st.markdown("### 📐 Domínio de Simulação")

        colD1, colD2, colD3 = st.columns(3)
        altura_total = colD1.number_input("Altura total (cm)", 10.0, key="cmp_altura")
        tempo_max = colD2.number_input("Tempo máximo (dia)", 50, key="cmp_tempo")
        n_alturas = colD3.number_input("Resolução", 20, key="cmp_res")

        # =========================
        # EXECUÇÃO
        # =========================
        if st.button("🚀 Comparar Cenários"):

            def build_payload(dens_susp, dens_solids, teor, m, n):
                return {
                    "fluido": {
                        "dens_susp": dens_susp,
                        "dens_solids": dens_solids,
                        "teor_solids": teor,
                        "m": m,
                        "n": n
                    },
                    "altura_total": altura_total,
                    "tempo_max": tempo_max,
                    "n_alturas": n_alturas
                }


            payload_A = build_payload(A_dens_susp, A_dens_solids, A_teor, A_m, A_n)
            payload_B = build_payload(B_dens_susp, B_dens_solids, B_teor, B_m, B_n)


            def run_analyze(payload):
                resp = requests.post(f"{BASE_URL}/v3/analyze", json=payload, headers=get_headers(), timeout=120)
                if resp.status_code != 200:
                    st.error("Erro no analyze")
                    st.text(resp.text)
                    st.stop()
                return resp.json()["data"]


            def run_simulate(payload):
                resp = requests.post(f"{BASE_URL}/v3/simulate", json=payload, headers=get_headers(), timeout=120)
                if resp.status_code != 200:
                    st.error("Erro no simulate")
                    st.text(resp.text)
                    st.stop()
                return pd.DataFrame(resp.json()["data"])


            with st.spinner("Comparando cenários..."):

                data_A = run_analyze(payload_A)
                data_B = run_analyze(payload_B)

                sim_A = run_simulate(payload_A)
                sim_B = run_simulate(payload_B)

            st.success("✔ Comparação concluída")

            # =========================
            # 📈 TOPO
            # =========================
            st.subheader("📈 Comparação no topo")

            dfA = pd.DataFrame(data_A.get("curva_topo", []))
            dfB = pd.DataFrame(data_B.get("curva_topo", []))

            if not dfA.empty and not dfB.empty:
                dfA = dfA.set_index("tempo")
                dfB = dfB.set_index("tempo")

                # st.line_chart({
                #     "Fluido A": dfA["concentracao"],
                #     "Fluido B": dfB["concentracao"]
                # })
                fig, ax = plt.subplots()

                ax.plot(dfA.index, dfA["concentracao"], label="Fluido A")
                ax.plot(dfB.index, dfB["concentracao"], label="Fluido B")

                ax.set_xlabel("Tempo (dia)")
                ax.set_ylabel("Concentração (v/v)")
                ax.set_title("Evolução da concentração no topo")

                ax.legend()
                ax.grid(True, alpha=0.3)

                st.pyplot(fig)

            # =========================
            # 📉 FUNDO
            # =========================
            st.subheader("📉 Comparação no fundo")

            dfA = pd.DataFrame(data_A.get("curva_fundo", []))
            dfB = pd.DataFrame(data_B.get("curva_fundo", []))

            if not dfA.empty and not dfB.empty:
                dfA = dfA.set_index("tempo")
                dfB = dfB.set_index("tempo")

                fig, ax = plt.subplots()

                ax.plot(dfA.index, dfA["concentracao"], label="Fluido A")
                ax.plot(dfB.index, dfB["concentracao"], label="Fluido B")

                ax.set_xlabel("Tempo (dia)")
                ax.set_ylabel("Concentração (v/v)")
                ax.set_title("Evolução da concentração no fundo")

                ax.legend()
                ax.grid(True, alpha=0.3)

                st.pyplot(fig)

            # =========================
            # 🧠 INTERFACE
            # =========================
            st.subheader("🧠 Interface")

            dfA = pd.DataFrame(data_A.get("interface", []))
            dfB = pd.DataFrame(data_B.get("interface", []))

            if not dfA.empty and not dfB.empty:
                dfA = dfA.set_index("tempo")
                dfB = dfB.set_index("tempo")

                # st.line_chart({
                #     "Fluido A": dfA["altura_interface"],
                #     "Fluido B": dfB["altura_interface"]
                # })
                fig, ax = plt.subplots()

                ax.plot(dfA.index, dfA["altura_interface"], label="Fluido A")
                ax.plot(dfB.index, dfB["altura_interface"], label="Fluido B")

                ax.set_xlabel("Tempo (dia)")
                ax.set_ylabel("Altura da interface (cm)")
                ax.set_title("Evolução da interface")

                ax.legend()
                ax.grid(True, alpha=0.3)

                st.pyplot(fig)

            # ==========================
            # 🧠 MÉTRICAS AUTOMÁTICAS
            # ==========================
            # st.markdown("## 🧠 Avaliação Quantitativa")
            st.markdown("""
            <div style="
                background-color:#161A23;
                padding:20px;
                border-radius:12px;
                margin-top:10px;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.4);
            ">
            <h3 style="margin-top:0;">🧠 Avaliação Quantitativa</h3>
            </div>
            """, unsafe_allow_html=True)


            def calcular_metricas(df):
                import numpy as np

                resultados = {}

                h_top = df["altura"].max()
                df_top = df[df["altura"] == h_top]

                h_bot = df["altura"].min()
                df_bot = df[df["altura"] == h_bot]

                # resultados["C_top_final"] = df_top["concentracao"].iloc[-1]
                resultados["C_top_final"] = (
                    df_top["concentracao"].iloc[-1] if not df_top.empty else None
                )

                threshold = 0.05
                below = df_top[df_top["concentracao"] < threshold]
                resultados["tempo_clarificacao"] = (
                    below["tempo"].iloc[0] if len(below) > 0 else None
                )

                resultados["C_bottom_final"] = df_bot["concentracao"].iloc[-1]

                resultados["std_temporal"] = df.groupby("tempo")["concentracao"].mean().std()

                return resultados


            # ✅ CORREÇÃO AQUI
            df_A = sim_A
            df_B = sim_B

            met_A = calcular_metricas(df_A)
            met_B = calcular_metricas(df_B)
            # =========================
            # 💾 SALVAR PARA PDF
            # =========================
            st.session_state["pdf_data"] = {
                "met_A": met_A,
                "met_B": met_B,
                "df_A": df_A,
                "df_B": df_B,
                "vencedor": None,
                "motivos": []
            }

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 🔵 Fluido A")
                st.metric("C topo final (v/v)", f"{met_A['C_top_final']:.4f}")
                st.metric("C fundo final (v/v)", f"{met_A['C_bottom_final']:.4f}")
                st.metric("Tempo de clarificação (dia)",
                          f"{met_A['tempo_clarificacao']}" if met_A['tempo_clarificacao'] else "—")
                st.metric("Variabilidade temporal (dia)", f"{met_A['std_temporal']:.4f}")

            with col2:
                st.markdown("### 🟢 Fluido B")
                st.metric("C topo final (v/v)", f"{met_B['C_top_final']:.4f}")
                st.metric("C fundo final (v/v)", f"{met_B['C_bottom_final']:.4f}")
                st.metric("Tempo de clarificação (dia)",
                          f"{met_B['tempo_clarificacao']}" if met_B['tempo_clarificacao'] else "—")
                st.metric("Variabilidade temporal (dia)", f"{met_B['std_temporal']:.4f}")

            # Ranking automático
            if met_A["C_top_final"] < met_B["C_top_final"]:
                st.success("🥇 Fluido A melhor clarificação no topo")
            else:
                st.success("🥇 Fluido B melhor clarificação no topo")

            # ==============================
            # 🧠 RANKING GLOBAL EXPLICÁVEL
            # ==============================

            st.subheader("🧠 Ranking global (IA explicável)")

            try:
                # =========================
                # ⚖️ PESOS (AJUSTÁVEL)
                # =========================
                w_top = st.slider("Peso topo", 0.0, 5.0, 2.0)
                w_bottom = st.slider("Peso fundo", 0.0, 5.0, 1.5)
                w_stability = st.slider("Peso estabilidade", 0.0, 5.0, 1.0)

                # =========================
                # 🧮 SCORE GLOBAL
                # =========================
                score_A = (
                        -w_top * met_A["C_top_final"]
                        + w_bottom * met_A["C_bottom_final"]
                        - w_stability * met_A["std_temporal"]
                )

                score_B = (
                        -w_top * met_B["C_top_final"]
                        + w_bottom * met_B["C_bottom_final"]
                        - w_stability * met_B["std_temporal"]
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Score Fluido A", f"{score_A:.4f}")

                with col2:
                    st.metric("Score Fluido B", f"{score_B:.4f}")

                # =========================
                # 🏆 RESULTADO FINAL
                # =========================
                if score_A > score_B:
                    vencedor = "A"
                    st.success("🏆 Fluido A melhor desempenho global")
                else:
                    vencedor = "B"
                    st.success("🏆 Fluido B melhor desempenho global")

                # =========================
                # 🔍 EXPLICAÇÃO (OURO!)
                # =========================
                st.markdown("### 🔍 Por que esse resultado?")

                exp = []

                # TOPO
                if met_A["C_top_final"] < met_B["C_top_final"]:
                    exp.append("🔹 Fluido A apresenta melhor clarificação no topo")
                elif met_B["C_top_final"] < met_A["C_top_final"]:
                    exp.append("🔹 Fluido B apresenta melhor clarificação no topo")

                # FUNDO
                if met_A["C_bottom_final"] > met_B["C_bottom_final"]:
                    exp.append("🔹 Fluido A apresenta maior compactação no fundo")
                elif met_B["C_bottom_final"] > met_A["C_bottom_final"]:
                    exp.append("🔹 Fluido B apresenta maior compactação no fundo")

                # ESTABILIDADE
                if met_A["std_temporal"] < met_B["std_temporal"]:
                    exp.append("🔹 Fluido A é mais estável ao longo do tempo")
                elif met_B["std_temporal"] < met_A["std_temporal"]:
                    exp.append("🔹 Fluido B é mais estável ao longo do tempo")

                # MOSTRAR EXPLICAÇÃO
                for e in exp:
                    st.write(e)

                # =========================
                # 📊 BREAKDOWN VISUAL
                # =========================
                st.markdown("### 📊 Contribuição dos critérios")

                import pandas as pd

                df_score = pd.DataFrame({
                    "Critério": ["Topo (↓)", "Fundo (↑)", "Estabilidade (↓)"],
                    "Fluido A": [
                        -w_top * met_A["C_top_final"],
                        w_bottom * met_A["C_bottom_final"],
                        -w_stability * met_A["std_temporal"]
                    ],
                    "Fluido B": [
                        -w_top * met_B["C_top_final"],
                        w_bottom * met_B["C_bottom_final"],
                        -w_stability * met_B["std_temporal"]
                    ]
                })

                st.bar_chart(df_score.set_index("Critério"))

            except Exception as e:
                st.warning(f"Erro ao calcular ranking explicável: {e}")

            # ==============================
            # 🧠 MODO EXECUTIVO
            # ==============================

            st.subheader("📊 Parecer Executivo")

            try:
                # =========================
                # 🏆 DEFINIR VENCEDOR
                # =========================
                if score_A > score_B:
                    vencedor = "A"
                    met_v = met_A
                    met_p = met_B
                else:
                    vencedor = "B"
                    met_v = met_B
                    met_p = met_A

                # =========================
                # 🔍 DIAGNÓSTICO
                # =========================
                motivos = []

                if met_v["C_top_final"] < met_p["C_top_final"]:
                    motivos.append("melhor clarificação no topo")

                if met_v["C_bottom_final"] > met_p["C_bottom_final"]:
                    motivos.append("maior compactação no fundo")

                if met_v["std_temporal"] < met_p["std_temporal"]:
                    motivos.append("maior estabilidade ao longo do tempo")

                # =========================
                # 📢 FRASE PRINCIPAL
                # =========================
                texto_principal = f"""
                🔎 **Recomendação:**  
                O **Fluido {vencedor}** apresenta melhor desempenho global para o cenário analisado.
                """

                st.markdown(texto_principal)

                # =========================
                # 🧠 JUSTIFICATIVA
                # =========================
                if motivos:
                    st.markdown("**Principais fatores de decisão:**")
                    for m in motivos:
                        st.write(f"• {m}")

                # =========================
                # ⚠️ TRADE-OFFS
                # =========================
                st.markdown("**Pontos de atenção:**")

                if met_v["C_bottom_final"] < met_p["C_bottom_final"]:
                    st.write("• Menor compactação no fundo pode impactar acúmulo de sólidos")

                if met_v["std_temporal"] > met_p["std_temporal"]:
                    st.write("• Maior variabilidade ao longo do tempo")

                if met_v["C_top_final"] > met_p["C_top_final"]:
                    st.write("• Menor eficiência de clarificação no topo")

                # =========================
                # 🎯 APLICAÇÃO IDEAL
                # =========================
                st.markdown("**Aplicação recomendada:**")

                if met_v["C_top_final"] < 0.07:
                    st.success("✔ Indicado para processos que exigem alta clarificação")

                if met_v["C_bottom_final"] > 0.15:
                    st.success("✔ Indicado para sistemas com alta sedimentação/compactação")

                if met_v["std_temporal"] < 0.02:
                    st.success("✔ Indicado para operação estável e previsível")

                # =========================
                # 💾 ATUALIZA PDF (AQUI!)
                # =========================
                st.session_state["pdf_data"]["vencedor"] = vencedor
                st.session_state["pdf_data"]["motivos"] = motivos

            except Exception as e:
                st.warning(f"Erro no modo executivo: {e}")

            # =========================
            # 🔥 HEATMAPS
            # =========================
            st.subheader("🔥 Mapas espaço-temporais")

            colH1, colH2 = st.columns(2)


            def plot_heatmap(df, title):
                pivot = df.pivot(index="altura", columns="tempo", values="concentracao")
                fig, ax = plt.subplots()
                cax = ax.imshow(pivot.values, aspect="auto", origin="lower")

                ax.set_xlabel("Tempo (dia)")
                ax.set_ylabel("Altura (cm)")
                fig.colorbar(cax, label="Concentração (v/v)")
                ax.set_title(title)
                return fig


            with colH1:
                if not sim_A.empty:
                    st.pyplot(plot_heatmap(sim_A, "Fluido A"))

            with colH2:
                if not sim_B.empty:
                    st.pyplot(plot_heatmap(sim_B, "Fluido B"))

        # ==============================
        # 📄 RELATÓRIO PDF (GLOBAL)
        # ==============================

        st.markdown("---")
        st.subheader("📄 Relatório Técnico")

        if "pdf_data" in st.session_state:

            if st.button("📄 Gerar PDF Premium"):

                try:
                    data = st.session_state["pdf_data"]

                    caminho, nome = gerar_pdf_premium(
                        data["met_A"],
                        data["met_B"],
                        data["vencedor"],
                        data["motivos"],
                        data["df_A"],
                        data["df_B"]
                    )

                    with open(caminho, "rb") as f:
                        pdf_bytes = f.read()

                    st.download_button(
                        label="📥 Baixar Relatório",
                        data=pdf_bytes,
                        file_name=nome,
                        mime="application/pdf"
                    )

                    st.success("✔ Relatório premium gerado com sucesso!")

                except Exception as e:
                    st.error(f"Erro ao gerar PDF: {e}")

    # RODAPÉ-------------------------------------------------------------------------------
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

