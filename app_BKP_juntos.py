import streamlit as st
import requests, base64, tempfile, os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import io
from io import BytesIO
from PIL import Image as PILImage
import pandas as pd
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import matplotlib.pyplot as plt
import json
from reportlab.lib import colors
import plotly.graph_objects as go

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
    token = st.session_state.get("token", "")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

#------------------------------------------------------------

# CONFIG DO STREMLIT -----------------
st.set_page_config(
    layout="wide",
    page_title="OptiGen",
    page_icon="🔬"
)

#===================================================
# SEGURANÇA/USUÁRIO/SENHA DE ACESSO
#===================================================

### Tela de login
st.markdown("<br><br><br>", unsafe_allow_html=True)

### --- LOGIN LOCAL:
# API_URL = "http://127.0.0.1:8010"  # ou localhost

## ------------------- LOGIN NA PRODUÇÃO (ONLINE NO RENDER) >>> deploy:
# API_URL = "https://optigen.onrender.com"
# st.write("DEBUG API_URL:", API_URL)

## --- LOGIN GLOBAL:
API_URL = os.getenv("API_URL", "http://127.0.0.1:8010")
# API_URL = st.secrets.get("API_URL", "http://127.0.0.1:8010")

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

        username = st.text_input("User")
        password = st.text_input("Password", type="password")

        if st.button("Enter", use_container_width=True):

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

                # --- BUSCAR PERMISSÕES DO USUÁRIO ---
                try:
                    # Chamamos a nova rota que criamos no backend
                    user_info_res = requests.get(f"{API_URL}/auth/me", headers=get_headers())
                    if user_info_res.status_code == 200:
                        user_data = user_info_res.json()
                        st.session_state.user_modules = user_data.get("modules", [])
                        st.session_state.user_plan = user_data.get("plan_type", "standard")
                        st.session_state.user_id = user_data.get("id") # Salva o id (UUID) exato do Supabase na sessão
                        st.session_state.username = user_data.get("username") # Salva o username
                        st.session_state.full_name = user_data.get("full_name") # Salva o nome completo
                    else:
                        st.session_state.user_modules = []
                except Exception as e:
                    st.error(f"Erro ao carregar permissões: {e}")
                    st.session_state.user_modules = []

                st.success("Login realizado!")
                st.rerun()

            else:
                st.error(f"Erro {response.status_code}")
                st.text(response.text)

    # with col3:
    #     st.image("assets/IA_login.png", width=200)


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

    # ==================================================================================================================

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

    col1, col2, col3 = st.columns([1, 3, 1])

    with col2:
        st.markdown(
            "<div style='margin-top:-100px;'>"
            "<h1 style='margin-bottom:5px;'>🔬 OptiGen</h1>"
            "<p style='font-size:20px; margin-top:-20px; margin-bottom:5px;'>"
            "Plataforma de Inteligência e Otimização em Engenharia Industrial"
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
    st.sidebar.markdown("<div style='height:50px'></div>", unsafe_allow_html=True)
    # Inserir botão logomarca na sidebar (desativar a linha abaixo se não desejar):
    # st.sidebar.image("assets/logo_newgen_black.png", width=80)

    # st.sidebar.markdown("""
    # <div style='margin-top:-110px;'>
    # </div>
    # <div style="line-height: 1.2; padding-bottom:10px;">
    #     <span style="font-size:20px; font-weight:600;">NewGen</span><br>
    #     <span style="font-size:15px; color:gray;">Intelligent Engineering Solutions</span>
    # </div>
    # <hr style="margin-top:-8px; margin-bottom:10px;">
    # """, unsafe_allow_html=True)

    st.sidebar.markdown(
        """
        <div style="margin-top:-110px;"></div>
        <div style="line-height: 1.2; padding-bottom:10px;">
            <span style="font-size:20px; font-weight:600;">
                <span style="color:red;">New</span><span style="color:white;">Gen</span>
            </span><br>
            <span style="font-size:15px; color:white;">Intelligent Engineering Solutions</span>
        </div>
        <hr style="margin-top:-8px; margin-bottom:10px;">
        """,
        unsafe_allow_html=True
    )

    # --- SEÇÃO DE PERFIL DO USUÁRIO (TOPO COMPACTO) ---
    username = st.session_state.get("username", "Usuário")
    full_name = st.session_state.get("full_name", "")

    st.sidebar.markdown(f"""
    <div style="margin-bottom: -15px; margin-top:-70px;">
        <h3 style="margin-bottom: -12px;">👤 Meu Perfil</h3>
        <p style="margin-bottom: 2px; font-size: 14px;"><b>Usuário:</b> {username}</p>
        {"<p style='margin-bottom: 2px; font-size: 14px;'><b>Nome:</b> " + full_name + "</p>" if full_name else ""}
        <hr style="margin-top:8px; margin-bottom:80px;">
    </div>
    """, unsafe_allow_html=True)

    # st.sidebar.markdown("---")

    # --- NAVEGAÇÃO DINÂMICA ---
    # st.sidebar.title("Plataforma de Simulação Inteligente")
    # st.sidebar.caption("Plataforma de Simulação Inteligente")
    st.sidebar.markdown("### Plataforma de Simulação Inteligente:")

    # Recupera os módulos que salvamos no login
    user_modules = st.session_state.get("user_modules", [])

    opcoes_menu = []

    # Se o usuário tem o módulo de simulação, libera as 4 opções de fluidos
    if "fluid_simulation" in user_modules:
        opcoes_menu.extend([
            "Eng. de Fluidos (Dados Exp.)",
            "Eng. de Fluidos (Comparação: Dados Exp.)",
            "Simulação Inteligente de Fluidos",
            "Simulação: Fluidos (A vs. B)"
        ])

    # Se o usuário tem o módulo de IT, libera a opção do Agente
    if "it_agent" in user_modules:
        opcoes_menu.append("Instruções de Trabalho")

    if "performance_academy" in user_modules or "it_agent" in user_modules:
        opcoes_menu.append("Jornada do Conhecimento")  # Academia ITO (Performance & Learning)

    # Renderiza o menu apenas se houver opções disponíveis
    if opcoes_menu:
        modo = st.sidebar.radio("Selecione um Módulo", opcoes_menu)
    else:
        st.sidebar.warning("⚠️ Nenhum módulo contratado.")
        st.info("Entre em contato com o suporte para ativar seus módulos.")
        st.stop()  # Interrompe a execução para não mostrar conteúdo vazio

    # st.sidebar.markdown("---")
    # st.sidebar.title("Configurações")
    #
    # save = st.sidebar.checkbox("Salvar imagem no servidor", True)
    # show_metadata = st.sidebar.checkbox("Mostrar metadados", True)
    #
    # if "history" not in st.session_state:
    #     st.session_state.history = []
    #
    # st.sidebar.markdown("### 📁 Histórico de Simulações")
    # for item in st.session_state.history:
    #     st.sidebar.markdown(
    #         f"• **Fluido {item['fluid_id']}**"
    #         f" → Altura: `{item['height']}`"
    #     )

    # Botão de logout (sair):
    logout = st.sidebar.button("Sair", help="Encerrar sessão")

    if logout:
        # Limpeza profunda da sessão ao sair
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown("""
        <style>
        /* Botão pequeno e discreto */
        button[kind="secondary"], button[kind="primary"] {
            font-size: 12px !important;
            padding: 4px 8px !important;
            border-radius: 10px !important;
        }

        /* Botão de topo mais leve */
        button {
            opacity: 0.2;
        }
        button:hover {
            opacity: 1;
        }
        </style>
        """, unsafe_allow_html=True)


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
    # pdf
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

        # 🔚 FINALIZA O pdf
        doc.build(elements)

        with open(temp_pdf.name, "rb") as f:
            return f.read()


    # ===============================
    # pdf DO CERTIFICADO (Certificado obtido da aprovação na Jornada de Aprendizado com as IT's)
    # ===============================
    def gerar_certificado_pdf(user_name, it_title, score, approved_pillars=None):
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        doc = SimpleDocTemplate(temp_pdf.name, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = [
            RLImage("assets/logo_newgen_white.png", width=140, height=110) if os.path.exists(
                "assets/logo_newgen_white.png") else Spacer(1, 1),
            Spacer(1, 24),
            Paragraph("CERTIFICADO DE CONCLUSÃO", styles["Title"]),
            Spacer(1, 24),
            Paragraph(f"Certificamos que", styles["Heading2"]),
            Spacer(1, 12),
            Paragraph(f"<b>{user_name.upper()}</b>", styles["Heading1"]),
            Spacer(1, 12),
            Paragraph(f"concluiu com sucesso o treinamento:", styles["Heading2"]),
            Spacer(1, 12),
            Paragraph(f"<b>{it_title}</b>", styles["Heading2"]),
            Spacer(1, 12),
            Paragraph(f"com a pontuação de <b>{score:.2f}/10</b>.", styles["Heading2"]),
        ]

        # Adiciona lista de pilares aprovados se disponível
        if approved_pillars:
            elements.append(Spacer(1, 12))
            elements.append(Paragraph("Pilares de Performance Aprovados:", styles["Heading2"]))
            for pillar in approved_pillars:
                elements.append(Paragraph(f"• {pillar}", styles["Normal"]))

        elements.extend([
            Spacer(1, 36),
            Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y')}", styles["Normal"]),
            Spacer(1, 48),
            Paragraph("_________________________________________", styles["Normal"]),
            Paragraph("NewGen Intelligent Engineering Solutions", styles["Normal"])
        ])
        doc.build(elements)
        with open(temp_pdf.name, "rb") as f: return f.read()


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
    # 📄 pdf PREMIUM - OPTIGEN
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
            content.append(RLImage(logo_path, width=140, height=110)) # width=120, height=60

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
    @st.cache_data(ttl=600) # Cache limpa a cada 10 min para evitar erros persistentes
    def get_fluids(token): # Adicionamos o token para tornar o cache individual
        headers = {"Authorization": f"Bearer {token}"}
        try:
            # Chamada direta para evitar o st.error global do safe_request
            response = requests.get(f"{BASE_URL}/profiles/available_fluids", headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                return data.get("fluids", [])
            return []
        except:
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
    # MODO (Movido para a Sidebar)
    # ===============================
    # --- CARGA DE DADOS POR MÓDULO ---
    user_modules = st.session_state.get("user_modules", [])

    # Inicializamos os dados dos módulos como vazios
    fluids = []
    hdt_data = []  # Exemplo para o futuro
    treinamento_data = []  # Exemplo para o futuro

    # Só carregamos os dados se o usuário possuir o módulo contratado
    if "fluid_simulation" in user_modules:
        fluids = get_fluids(st.session_state.token)
        if not fluids:
            st.warning("⚠️ Módulo de Simulação ativo, mas nenhum fluido encontrado no banco.")

    # SEGURANÇA FINAL: Só para se o usuário não tiver NADA
    if not user_modules:
        st.error("🚫 Nenhum módulo contratado encontrado para sua conta.")
        st.info("Por favor, entre em contato com o suporte da NewGen.")
        st.stop()

    # ===============================
    # MODO INDIVIDUAL
    # ===============================
    if modo == "Eng. de Fluidos (Dados Exp.)":
        st.markdown("## 📊 Análise de Perfil Estático")
        st.markdown("""
            <div style='background-color: #161A23; padding: 15px; border-left: 5px solid #E50914; border-radius: 5px;'>
                <p style='margin: 0; color: #A0A0A0;'>
                    <b>Exploração detalhada de perfis de sedimentação em fluidos de perfuração de poços de petróleo. Visualize curvas de concentração e metadados técnicos por altura.</b>
                </p>
            </div>

                """, unsafe_allow_html=True)
        st.markdown("---")

        # ---------------------------------------
        if not fluids:
            st.info("💡 Selecione um módulo no menu lateral ou aguarde o carregamento dos dados.")
            st.stop()
        # ---------------------------------------

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
    elif modo == "Eng. de Fluidos (Comparação: Dados Exp.)":
        st.markdown("## ⚖️ Benchmark de Estabilidade")
        st.markdown("""
            <div style='background-color: #161A23; padding: 15px; border-left: 5px solid #E50914; border-radius: 5px;'>
                <p style='margin: 0; color: #A0A0A0;'>
                    <b>Compare múltiplos fluidos simultaneamente. Identifique variações de performance entre amostras distintas.</b>
                </p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("---")

        if not fluids:
            st.info("💡 Este módulo requer dados de fluidos que não estão disponíveis para seu perfil.")
            st.stop()

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
    if modo == "Simulação Inteligente de Fluidos":

        st.markdown("## 🧠 Motor Preditivo OptiGen")
        st.markdown("""
            <div style='background-color: #161A23; padding: 15px; border-left: 5px solid #E50914; border-radius: 5px;'>
                <p style='margin: 0; color: #A0A0A0;'>
                    <b>Modelagem Híbrida (Físico + Data-Driven):</b> Estime a evolução espaço-temporal da concentração, 
                    perfis de interface e tempos de clareamento com precisão industrial.
                </p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("---")

        # --- ADICIONE O ESCUDO AQUI ---
        if "fluid_simulation" not in st.session_state.get("user_modules", []):
            st.info("💡 Este módulo de IA requer o plano de Simulação Inteligente.")
            st.stop()
        # ------------------------------

        st.subheader("Simulação Inteligente de Sedimentação")
        st.info("Simulação baseada em modelo físico–data-driven")

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
                    st.subheader("📊 Perfil inicial (em t=0) com c(v/v) vs. h(cm)")
                    st.line_chart(df_profile.set_index("altura")["concentracao"])
                else:
                    st.warning("Sem dados para perfil inicial")

                # =========================
                # 📈 TOPO
                # =========================
                df_top = pd.DataFrame(data.get("curva_topo", []))

                if not df_top.empty:
                    st.subheader("📈 Evolução no topo com c(v/v) vs. t(dia)")
                    st.line_chart(df_top.set_index("tempo")["concentracao"])
                else:
                    st.warning("Sem dados para curva do topo")

                # =========================
                # 📉 FUNDO
                # =========================
                df_bottom = pd.DataFrame(data.get("curva_fundo", []))

                if not df_bottom.empty:
                    st.subheader("📉 Evolução no fundo com c(v/v) vs. t(dia)")
                    st.line_chart(df_bottom.set_index("tempo")["concentracao"])
                else:
                    st.warning("Sem dados para curva do fundo")

                # =========================
                # 🧠 INTERFACE
                # =========================
                df_interface = pd.DataFrame(data.get("interface", []))

                if not df_interface.empty:
                    st.subheader("🧠 Evolução da Interface de Sedimentação, com h_interface(cm) vs. t(dia)")
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
    elif modo == "Simulação: Fluidos (A vs. B)":

        st.markdown("## 🚀 Arena de Cenários: Duelo Técnico Entre Fluidos")
        st.markdown("""
            <div style='background-color: #161A23; padding: 15px; border-left: 5px solid #E50914; border-radius: 5px;'>
                <p style='margin: 0; color: #A0A0A0;'>
                    <b>O motor de IA analisa compactação e estabilidade para recomendar o melhor setup operacional.</b>
                </p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("---")

        # --- ADICIONE O ESCUDO AQUI ---
        if "fluid_simulation" not in st.session_state.get("user_modules", []):
            st.info("💡 Este módulo de comparação de IA requer o plano de Simulação Inteligente.")
            st.stop()
            # ------------------------------

        st.info("Compare dois cenários físicos–data-driven e identifique o melhor comportamento")

        # =========================
        # INPUTS - FLUIDO A
        # =========================
        st.markdown("### 🅰️ Fluido A")

        colA1, colA2, colA3 = st.columns(3)
        A_dens_susp = colA1.number_input("dens_susp (g/cm³)", 1.6e-4, key="A_dens_susp")
        A_dens_solids = colA2.number_input("dens_solids (g/cm³)", 1.6e-4, key="A_dens_solids")
        A_teor = colA3.number_input("teor_solids (fração)", 1.0e-3, key="A_teor")

        colA4, colA5 = st.columns(2)
        A_m = colA4.number_input("m (reologia)", 1.0e-3, key="A_m")
        A_n = colA5.number_input("n (reologia)", 1.0e-3, key="A_n")
        # Na equação tau = m*(gamma)^n, o parâmetro m (índice de consistência) exige valores m > 0.
        # O parâmetro m reflete o nível de consistência do fluido (uma analogia à viscosidade).
        # Fisicamente, a consistência não pode ser nula ou negativa.
        # O parâmetro n classifica o fluido:
        # n = 1 (fluido newtoniano: a viscosidade se mantém constante, independentemente da taxa de deformação);
        # n < 1 (fluido pseudoplástico: a viscosidade diminui conforme o fluido é cisalhado. Na grande maioria das aplicações e substâncias naturais, n é um valor decimal positivo (0 < n < 1).
        # n > 1 (fluido dilatante: a viscosidade aumenta conforme a taxa de cisalhamento eleva-se).
        # Valores físicos reais de n são sempre maiores que zero.

        # =========================
        # INPUTS - FLUIDO B
        # =========================
        st.markdown("### 🅱️ Fluido B")

        colB1, colB2, colB3 = st.columns(3)
        B_dens_susp = colB1.number_input("dens_susp (g/cm³)", 1.6e-4, key="B_dens_susp")
        B_dens_solids = colB2.number_input("dens_solids (g/cm³)", 1.6e-4, key="B_dens_solids")
        B_teor = colB3.number_input("teor_solids (fração)", 1.0e-3, key="B_teor")

        colB4, colB5 = st.columns(2)
        B_m = colB4.number_input("m (reologia)", 1.0e-3, key="B_m")
        B_n = colB5.number_input("n (reologia)", 1.0e-3, key="B_n")

        # =========================
        # DOMÍNIO
        # =========================
        st.markdown("### 📐 Domínio de Simulação")

        colD1, colD2, colD3 = st.columns(3)
        altura_total = colD1.number_input("Altura total (cm)", 5.0, key="cmp_altura")
        tempo_max = colD2.number_input("Tempo máximo (dia)", 10, key="cmp_tempo")
        n_alturas = colD3.number_input("Resolução", 10, key="cmp_res")

        # =======================================================================================================
        # EXECUÇÃO
        # =======================================================================================================

        # ========================
        # 🎯 OBJETIVO DO PROCESSO
        # ========================

        st.markdown("### 🎯 Objetivo do Processo")

        objetivo = st.selectbox(
            "Selecione o objetivo da operação",
            [
                "Balanceado",
                "Máxima clarificação",
                "Máxima compactação",
                "Estabilidade operacional"
            ]
        )
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


            # =========================================================
            # 🎨 CLASSIFICAÇÃO VISUAL (INDICADORES)
            # =========================================================
            def classificar_clarificacao(c):
                if c is None:
                    return "—"
                elif c < 0.05:
                    return "🟢 Excelente"
                elif c < 0.1:
                    return "🟡 Moderada"
                else:
                    return "🔴 Baixa"


            def calcular_metricas(df):

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
            # 💾 SALVAR PARA pdf
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
                # st.metric("C topo final (v/v)", f"{met_A['C_top_final']:.4f}")
                st.metric(
                    "C topo final (v/v)",
                    f"{met_A['C_top_final']:.4f}",
                    classificar_clarificacao(met_A["C_top_final"])
                )
                st.metric("C fundo final (v/v)", f"{met_A['C_bottom_final']:.4f}")
                st.metric("Tempo de clarificação (dia)",
                          f"{met_A['tempo_clarificacao']}" if met_A['tempo_clarificacao'] else "—")
                st.metric("Variabilidade temporal (dia)", f"{met_A['std_temporal']:.4f}")

            with col2:
                st.markdown("### 🟢 Fluido B")
                # st.metric("C topo final (v/v)", f"{met_B['C_top_final']:.4f}")
                st.metric(
                    "C topo final (v/v)",
                    f"{met_B['C_top_final']:.4f}",
                    classificar_clarificacao(met_B["C_top_final"])
                )
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
                # =========================================================
                # ⚖️ DEFINIÇÃO AUTOMÁTICA DE PESOS
                # =========================================================

                if objetivo == "Máxima clarificação":
                    w_top = 3.0
                    w_bottom = 1.0
                    w_stability = 1.0

                elif objetivo == "Máxima compactação":
                    w_top = 1.0
                    w_bottom = 3.0
                    w_stability = 1.0

                elif objetivo == "Estabilidade operacional":
                    w_top = 1.0
                    w_bottom = 1.0
                    w_stability = 3.0

                else:  # Balanceado
                    w_top = 2.0
                    w_bottom = 1.5
                    w_stability = 1.0

                st.caption(
                    f"Pesos aplicados → Topo: {w_top} | Fundo: {w_bottom} | Estabilidade: {w_stability}"
                )

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
                # st.markdown("### 🔍 Por que esse resultado?")
                st.markdown("### 🔍 Interpretação do Resultado")

                st.write(f"O resultado foi avaliado com foco em: **{objetivo}**")

                exp = []

                # TOPO
                if met_A["C_top_final"] < met_B["C_top_final"]:
                    exp.append("🔹 Fluido A apresenta maior eficiência na redução de concentração no topo (melhor clarificação)")
                elif met_B["C_top_final"] < met_A["C_top_final"]:
                    exp.append("🔹 Fluido B apresenta maior eficiência na redução de concentração no topo (melhor clarificação)")

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
                # 💾 ATUALIZA pdf (AQUI!)
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
        # 📄 RELATÓRIO pdf (GLOBAL)
        # ==============================

        st.markdown("---")
        st.subheader("📄 Relatório Técnico")

        if "pdf_data" in st.session_state:

            if st.button("📄 Gerar pdf Premium"):

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
                    st.error(f"Erro ao gerar pdf: {e}")

    # ==================================================================================================================
    # 📝 MODO Agente de IA - Instruções de Trabalho (IT)
    # ==================================================================================================================
    elif modo == "Instruções de Trabalho":

        def render_it_module(API_URL, headers):

            st.markdown("## 📋 Agente de Inteligência Operacional e Instruções de Trabalho (IT)")
            st.markdown("""
                <div style='background-color: #161A23; padding: 15px; border-left: 5px solid #E50914; border-radius: 5px;'>
                    <p style='margin: 0; color: #A0A0A0;'>
                        <b>Transforme manuais e relatos em Instruções de Trabalho estruturadas com foco total em Segurança e Controles Críticos.</b>
                    </p>
                </div>

                """, unsafe_allow_html=True)
            st.markdown(
                "<p style='text-align: left; color: gray;'>Padrão Industrial - Gestão de Conhecimento e Segurança</p>",
                unsafe_allow_html=True)
            st.markdown("---")

            # --- INGESTÃO DE DADOS ---
            st.markdown("### 📥 Ingestão de Dados Multimodal")
            tabs = st.tabs(["📄 Documentos (pdf/Word)", "🎙️ Áudio / Vídeo", "⌨️ Texto / Transcrição"])

            with tabs[0]:
                st.info("💡 Arraste manuais técnicos ou normas para converter em IT.")
                doc_file = st.file_uploader("Carregar Documento", type=["pdf", "docx"], key="doc_up")

            with tabs[1]:
                st.info("💡 Suba relatos de campo ou vídeos de execução de tarefas.")
                media_file = st.file_uploader("Carregar Mídia", type=["mp3", "wav", "mp4", "mov", "m4a"],
                                              key="media_up")

            with tabs[2]:
                text_content = st.text_area("Descreva a atividade detalhadamente:", height=200,
                                            placeholder="Ex: Procedimento para manutenção preventiva da bomba de vácuo...")

            filename_prefix = st.text_input("Nome sugerido para a IT", value="IT_Nova_Atividade")

            # Lógica de seleção do arquivo para envio
            final_file = None
            if doc_file:
                final_file = doc_file
            elif media_file:
                final_file = media_file
            elif text_content:
                final_file = io.BytesIO(text_content.encode('utf-8'))
                final_file.name = "input.txt"

            # --- BOTÃO DE PROCESSAMENTO ---
            if st.button("🚀 Processar e Gerar IT Oficial", use_container_width=True, type="primary"):
                if not final_file:
                    st.warning("Por favor, forneça uma entrada (arquivo ou texto).")
                else:
                    with st.spinner("🤖 O Agente OptiGen está analisando e estruturando a IT..."):
                        try:

                            # 1. Criamos um cabeçalho que só tem o Token (sem o application/json)
                            headers_it = {"Authorization": f"Bearer {st.session_state.token}"}

                            files = {"file": (final_file.name, final_file, "application/octet-stream")}
                            data = {"filename_prefix": filename_prefix}

                            # 2. Chamada para o endpoint atualizado
                            response = requests.post(
                                f"{API_URL}/it/generate",
                                files=files,
                                data=data,
                                headers=headers_it,  # <-- Use o headers_it aqui
                                timeout=300
                            )

                            if response.status_code == 200:
                                st.session_state.current_it = response.json()
                                st.success("✅ Processamento concluído!")
                            else:
                                st.error(f"Erro no servidor: {response.text}")
                        except Exception as e:
                            st.error(f"Erro de conexão: {e}")

            # --- EXIBIÇÃO DOS RESULTADOS ---
            if "current_it" in st.session_state:
                res = st.session_state.current_it
                it = res["data"]
                pdf_url = res["pdf_url"]
                word_url = res.get("word_url", "")  # Pega a nova URL do Word se existir

                st.markdown("---")
                st.markdown(f"### 📋 IT Gerada: {it['titulo']}")

                # Matriz de Segurança
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.error("**🚨 RISCOS**\n\n" + "\n".join([f"- {r}" for r in it['matriz_seguranca']['riscos']]))
                with c2:
                    st.success("**✅ CONTROLES CRÍTICOS**\n\n" + "\n".join(
                        [f"- {c}" for c in it['matriz_seguranca']['controles_criticos']]))
                with c3:
                    st.warning("**⚠️ CRITÉRIOS DE PARADA**\n\n" + "\n".join(
                        [f"- {p}" for p in it['matriz_seguranca']['criterios_parada']]))

                # Fluxo de Trabalho
                with st.expander("👁️ Ver Fluxo de Execução Detalhado", expanded=True):
                    for step in it['fluxo_execucao']:
                        st.markdown(f"**Passo {step['passo_n']}: {step['o_que_fazer']}**")
                        st.info(f"**Como:** {step['como_fazer']}\n\n**Por que:** {step['por_que_fazer']}")
                        st.caption(f"🛡️ Controles de Segurança: {', '.join(step['medidas_controle'])}")
                        st.markdown("---")

                # --- DOWNLOADS ---
                st.markdown("### 📥 Baixar Documentos Oficiais")
                col_pdf, col_word = st.columns(2)

                with col_pdf:
                    full_pdf_url = f"{API_URL}{pdf_url}"
                    st.markdown(f"""
                        <a href="{full_pdf_url}" target="_blank" style="text-decoration: none;">
                            <button style="background-color: #E50914; color: white; border: none; padding: 12px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%;">
                                📕 Baixar em pdf
                            </button>
                        </a>
                    """, unsafe_allow_html=True)

                with col_word:
                    if word_url:
                        full_word_url = f"{API_URL}{word_url}"
                        st.markdown(f"""
                            <a href="{full_word_url}" target="_blank" style="text-decoration: none;">
                                <button style="background-color: #2B579A; color: white; border: none; padding: 12px; font-size: 16px; font-weight: bold; border-radius: 8px; cursor: pointer; width: 100%;">
                                    📘 Baixar em Word (Editável)
                                </button>
                            </a>
                        """, unsafe_allow_html=True)


        # Chamada da função para renderizar na tela
        render_it_module(API_URL, get_headers())

    elif modo == "Jornada do Conhecimento":

        def get_attempts_count(it_id, headers):
            try:
                response = requests.get(f"{API_URL}/performance/my-results", headers=headers)
                if response.status_code == 200:
                    results = response.json()

                    # Comparação robusta convertendo IDs para string
                    it_results = [r for r in results if str(r.get("it_id")) == str(it_id)]

                    count = len(it_results)
                    is_approved = any(r.get("status") == "Apto" for r in it_results)
                    return count, is_approved
                return 0, False
            except Exception as e:
                return 0, False


        def render_performance_module(API_URL, headers):
            # Inicialização segura do estado
            if "current_it_id" not in st.session_state: st.session_state.current_it_id = None
            if "current_it_title" not in st.session_state: st.session_state.current_it_title = "Capacitação"
            if "quiz_results_to_display" not in st.session_state: st.session_state.quiz_results_to_display = None
            if "quiz_completed" not in st.session_state: st.session_state.quiz_completed = False
            if "current_quiz" not in st.session_state: st.session_state.current_quiz = None

            st.markdown("## 🎓 OptiGen Performance & Learning (Academia ITO)")
            st.markdown("""
                <div style='background-color: #161A23; padding: 15px; border-left: 5px solid #007BFF; border-radius: 5px;'>
                    <p style='margin: 0; color: #A0A0A0;'>
                        <b>Metodologia ITO (Alumar):</b> Gestão de conhecimento, capacitação técnica e auditoria de performance baseada em 6 pilares estratégicos.
                    </p>
                </div>
            """, unsafe_allow_html=True)

            # TRAVA DE SEGURANÇA E PRIVACIDADE CIRÚRGICA
            user_plan = st.session_state.get("user_plan", "standard")
            username_logged = st.session_state.get("username", "").lower().strip()
            is_admin = user_plan == "admin" or username_logged == "admin"

            if is_admin:
                tabs = st.tabs(["📊 Dashboard ITO", "👨‍🏫 Área do Instrutor", "👷 Jornada do Operador", "📈 Matriz de Versatilidade", "💬 Consultar Especialista IA"])
                tab_dash, tab_inst, tab_op, tab_matrix, tab_chat = tabs
            else:
                tabs = st.tabs(["👷 Minha Jornada", "📈 Meu Perfil de Competências", "💬 Consultar Especialista IA"])
                tab_op, tab_matrix, tab_chat = tabs

            with tab_chat:
                st.subheader("💬 Agente de IA - Consultor Técnico de Campo")
                st.markdown("Tire suas dúvidas sobre os procedimentos e normas das ITs aprovadas.")

                # Busca ITs aprovadas para o contexto do chat
                try:
                    chat_its_res = requests.get(f"{API_URL}/performance/its?approved_only=True", headers=headers)
                    if chat_its_res.status_code == 200:
                        chat_its = chat_its_res.json()
                        if not chat_its:
                            st.info("Aguardando ITs aprovadas para consulta.")
                        else:
                            it_chat_options = {it["title"]: it["id"] for it in chat_its}
                            selected_chat_it = st.selectbox("Sobre qual IT você deseja tirar dúvidas?", list(it_chat_options.keys()))

                            # Chave única para o chat baseada no usuário e na IT selecionada
                            chat_key = f"chat_{st.session_state.get('user_id')}_{selected_chat_it}"
                            if chat_key not in st.session_state:
                                st.session_state[chat_key] = []

                            for msg in st.session_state[chat_key]:
                                with st.chat_message(msg["role"]):
                                    st.markdown(msg["content"])

                            if prompt := st.chat_input("Como posso ajudar com este procedimento?"):
                                st.session_state[chat_key].append({"role": "user", "content": prompt})
                                with st.chat_message("user"):
                                    st.markdown(prompt)

                                with st.chat_message("assistant"):
                                    with st.spinner("Consultando biblioteca técnica..."):
                                        # RAG Real: Busca o conteúdo da IT para servir de contexto
                                        it_data_res = requests.get(f"{API_URL}/performance/it-content/{it_chat_options[selected_chat_it]}", headers=headers)
                                        if it_data_res.status_code == 200:
                                            it_context = it_data_res.json()["content"]

                                            # Chamada para o Agente de IA (Usando o endpoint de geração de IT adaptado para Chat)
                                            # Aqui usamos o motor da IA para responder baseado no contexto
                                            chat_payload = {
                                                "it_context": str(it_context),
                                                "question": prompt
                                            }

                                            # Chamada para o Agente de IA (Usando o endpoint de geração de IT adaptado para Chat)
                                            # Aqui usamos o motor da IA para responder baseado no contexto
                                            chat_payload = {
                                                "it_id": it_chat_options[selected_chat_it], # Passamos o ID da IT
                                                "question": prompt
                                            }

                                            # Novo endpoint para o chat da IA
                                            ai_response = requests.post(f"{API_URL}/performance/chat-ia", json=chat_payload, headers=headers)

                                            if ai_response.status_code == 200:
                                                response_text = ai_response.json()["response"]
                                                st.markdown(response_text)
                                                st.session_state[chat_key].append({"role": "assistant", "content": response_text})
                                            else:
                                                st.error(f"Erro ao consultar o especialista de IA: {ai_response.json().get('detail', 'Erro desconhecido')}")
                                        else:
                                            st.error("Não consegui acessar o manual desta IT.")

                except Exception as e:
                    st.error(f"Erro no chat: {e}")

            # Definindo os 6 pilares oficiais da metodologia ITO
            all_pillars = ["Comportamento Seguro", "Consciência Ambiental", "ABS e RH", "Processo e Qualidade", "Manutenção", "Operação"]

            if is_admin:
                with tab_dash:
                    st.subheader("Maturidade Operacional por Pilar")
                    # Busca os dados da matriz para calcular a média geral
                    try:
                        matrix_res = requests.get(f"{API_URL}/performance/skills-matrix", headers=headers)
                        if matrix_res.status_code == 200:
                            matrix_data = matrix_res.json()
                            if matrix_data:
                                # Calcula a média dos scores por pilar para todos os operadores
                                pillar_averages = {p: [] for p in all_pillars}
                                for entry in matrix_data:
                                    p_scores = entry.get("pillar_scores", {})
                                    for pillar in all_pillars:
                                        if pillar in p_scores: # Verifica se o pilar existe nos scores do operador
                                            pillar_averages[pillar].append(p_scores[pillar])

                                # Filtro por Operador (Busca todos os usuários cadastrados)
                                try:
                                    # O endpoint correto agora existe em /users/
                                    users_resp = requests.get(f"{API_URL}/users/", headers=headers)
                                    if users_resp.status_code == 200:
                                        all_users_data = users_resp.json()
                                        all_operators = ["Todos os Operadores"] + sorted(list(set([u.get("username") for u in all_users_data if u.get("username")])))
                                    else:
                                        # Fallback para os nomes que já estão na matriz
                                        all_operators = ["Todos os Operadores"] + sorted(list(set([entry.get("operator_name") for entry in matrix_data if entry.get("operator_name")])))
                                except:
                                    all_operators = ["Todos os Operadores"] + sorted(list(set([entry.get("operator_name") for entry in matrix_data if entry.get("operator_name")])))

                                selected_op = st.selectbox("🎯 Filtrar Visão por Operador:", all_operators)
                                
                                if selected_op != "Todos os Operadores":
                                    # Filtra os dados comparando com operator_name (que é o campo que o backend retorna no skills-matrix)
                                    matrix_data = [entry for entry in matrix_data if entry.get("operator_name") == selected_op]
                                    
                                    # Recalcula as médias apenas para este operador
                                    pillar_averages = {p: [] for p in all_pillars}
                                    for entry in matrix_data:
                                        p_scores = entry.get("pillar_scores", {})
                                        for pillar in all_pillars:
                                            if pillar in p_scores:
                                                pillar_averages[pillar].append(p_scores[pillar])
                                    
                                    st.info(f"Exibindo Perfil de Competências de: **{selected_op}**")
                                else:
                                    st.info("Exibindo Média Geral de Maturidade da Equipe.")

                                # Calcula a média final para cada pilar
                                avg_values = [sum(pillar_averages[p]) / len(pillar_averages[p]) if pillar_averages[p] else 0 for p in all_pillars]

                                fig = go.Figure(data=go.Scatterpolar(r=avg_values, theta=all_pillars, fill='toself', name='Performance'))
                                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='grey'))
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.info("Nenhum resultado registrado para gerar o dashboard ainda.")
                        else:
                            st.error("Erro ao carregar dados para o dashboard.")
                    except Exception as e:
                        st.error(f"Erro ao gerar dashboard: {e}")

                with tab_inst:
                    st.subheader("👨‍🏫 Central do Instrutor Técnico")
                    st.info("💡 Aqui o Instrutor gera trilhas de aprendizagem a partir das ITs oficiais.")
                    try:
                        response = requests.get(f"{API_URL}/performance/its", headers=headers)
                        if response.status_code == 200:
                            available_its = response.json()
                            it_options = {it["title"]: it["id"] for it in available_its}
                            if not it_options:
                                st.warning("Nenhuma IT encontrada no banco de dados.")
                            else:
                                selected_it_title = st.selectbox("Selecione uma IT para gerar treinamento:", list(it_options.keys()))
                                selected_it_id = it_options[selected_it_title]
                                col_btn1, col_btn2, col_btn3 = st.columns(3)
                                with col_btn1:
                                    if st.button("🚀 Gerar Quiz via IA", key="generate_quiz_button", use_container_width=True):
                                        with st.spinner("🧠 Gerando Quiz..."):
                                            quiz_response = requests.post(f"{API_URL}/performance/generate-quiz/{selected_it_id}", headers=headers)
                                            if quiz_response.status_code == 200:
                                                st.success("✅ Quiz gerado!")
                                            else: st.error("Erro ao gerar quiz.")
                                
                                with col_btn2:
                                    if st.button("👁️ Visualizar IT", key="view_it_button", use_container_width=True):
                                        with st.spinner("Carregando conteúdo..."):
                                            v_res = requests.get(f"{API_URL}/performance/it-content/{selected_it_id}", headers=headers)
                                            if v_res.status_code == 200:
                                                st.session_state.preview_it = v_res.json()["content"]
                                                st.rerun()
                                            else: st.error("Erro ao carregar IT.")
                                
                                with col_btn3:
                                    if st.button("✅ Aprovar IT", key="approve_it_button", use_container_width=True, type="primary"):
                                        with st.spinner("Sincronizando..."):
                                            appr_res = requests.post(f"{API_URL}/performance/approve-it/{selected_it_id}", headers=headers)
                                            if appr_res.status_code == 200:
                                                st.success(f"✅ IT '{selected_it_title}' Aprovada!")
                                                st.balloons()
                                                st.info("Esta IT agora está disponível para os operadores na aba 'Jornada do Operador'.")
                                            else: st.error("Erro ao aprovar IT.")
                            
                            # --- QUEBRA DE CONTEXTO PARA FORÇAR LARGURA TOTAL ---
                            st.write("") 
                            
                            # Área de Preview da IT para o Supervisor (TOTALMENTE FORA DAS COLUNAS)
                            if "preview_it" in st.session_state and st.session_state.preview_it:
                                st.markdown("---")
                                with st.container(border=True):
                                    col_title, col_close = st.columns([0.9, 0.1])
                                    with col_title:
                                        st.markdown("### 🔍 Detalhamento Técnico da IT")
                                    with col_close:
                                        if st.button("✖️ Fechar", key="close_preview_top", use_container_width=True):
                                            st.session_state.preview_it = None
                                            st.rerun()
                                    
                                    it_prev = st.session_state.preview_it
                                    
                                    # Se for o texto bruto (RAG), tenta exibir de forma formatada ou JSON
                                    if "texto_bruto" in it_prev:
                                        with st.expander("Ver Conteúdo Bruto", expanded=True):
                                            st.text(it_prev["texto_bruto"])
                                    else:
                                        # Exibe o conteúdo estruturado da IT de forma organizada (Layout Amplo)
                                        st.info(f"#### 📄 {it_prev.get('titulo', 'Instrução de Trabalho')}")
                                        
                                        col_info1, col_info2 = st.columns([0.7, 0.3])
                                        with col_info1:
                                            st.markdown(f"**🎯 Objetivo:** {it_prev.get('objetivo', 'N/A')}")
                                        with col_info2:
                                            st.markdown(f"**📍 Local:** {it_prev.get('local', 'N/A')}")

                                        st.markdown("---")
                                        st.markdown("#### 🛡️ Matriz de Segurança")
                                        # Colunas com larguras iguais para evitar compressão
                                        col_r, col_c, col_p = st.columns(3, gap="medium")
                                        matriz = it_prev.get('matriz_seguranca', {})
                                        
                                        riscos = matriz.get('riscos', [])
                                        controles = matriz.get('controles_criticos', [])
                                        parada = matriz.get('criterios_parada', [])
                                        
                                        with col_r:
                                            st.error("**🚨 RISCOS**\n\n" + ("\n".join([f"- {r}" for r in riscos]) if riscos else "Nenhum risco mapeado."))
                                        with col_c:
                                            st.success("**✅ CONTROLES CRÍTICOS**\n\n" + ("\n".join([f"- {c}" for c in controles]) if controles else "Nenhum controle mapeado."))
                                        with col_p:
                                            st.warning("**⚠️ CRITÉRIOS DE PARADA**\n\n" + ("\n".join([f"- {p}" for p in parada]) if parada else "Nenhum critério de parada."))

                                        st.markdown("---")
                                        st.markdown("#### ⚙️ Fluxo de Execução")
                                        fluxo = it_prev.get('fluxo_execucao', [])
                                        if fluxo:
                                            for step in fluxo:
                                                with st.expander(f"**Passo {step.get('passo_n', 'N/A')}: {step.get('o_que_fazer', 'N/A')}**", expanded=True):
                                                    st.markdown(f"**🛠️ Como fazer:**\n{step.get('como_fazer', 'N/A')}")
                                                    st.markdown(f"**💡 Por que fazer:**\n{step.get('por_que_fazer', 'N/A')}")
                                                    medidas = step.get('medidas_controle', [])
                                                    if medidas:
                                                        st.caption(f"🛡️ Segurança: {', '.join(medidas)}")
                                        else:
                                            st.info("Nenhum passo de execução detalhado disponível.")
                                    
                                    if st.button("Fechar Visualização", key="close_preview_bottom", use_container_width=True):
                                        st.session_state.preview_it = None
                                        st.rerun()
                        else: st.error(f"Erro ao carregar ITs: {response.text}")
                    except Exception as e: st.error(f"Erro de conexão: {e}")

            with tab_op:
                st.subheader("👷 Minha Jornada de Conhecimento")
                if "current_quiz" not in st.session_state or st.session_state.current_quiz is None:
                    st.markdown("### 📚 Selecionar Treinamento")
                    try:
                        # Agora filtramos apenas ITs aprovadas para o operador
                        response = requests.get(f"{API_URL}/performance/its", params={"approved_only": "True"}, headers=headers)
                        if response.status_code == 200:
                            available_its = response.json()
                            it_options = {it["title"]: it["id"] for it in available_its}
                            if not it_options:
                                st.warning("⚠️ Nenhuma IT aprovada disponível para treinamento no momento.")
                            else:
                                selected_it_title = st.selectbox("Escolha a IT para iniciar:", list(it_options.keys()), key="op_it_select")
                                it_id = it_options[selected_it_title]

                                n_attempts, is_approved = get_attempts_count(it_id, headers)
                                if is_approved:
                                    st.success("✅ Você já foi aprovado(a) nesta IT. Parabéns!")
                                    st.button("🚀 Iniciar Quiz", key="op_start_quiz", disabled=True)
                                elif n_attempts >= 2:
                                    st.error(f"🚫 Limite de tentativas atingido ({n_attempts}/2). Não é possível iniciar um novo quiz para esta IT.")
                                    st.button("🚀 Iniciar Quiz", key="op_start_quiz", disabled=True)
                                else:
                                    if n_attempts == 1: st.warning("⚠️ Última chance! Esta é sua 2ª e última tentativa.")
                                    if st.button("🚀 Iniciar Quiz", key="op_start_quiz"):
                                        with st.spinner("🧠 Gerando Quiz..."):
                                            quiz_res = requests.post(f"{API_URL}/performance/generate-quiz/{it_id}", headers=headers)
                                            if quiz_res.status_code == 200:
                                                st.session_state.current_quiz = quiz_res.json().get("quiz", quiz_res.json())
                                                st.session_state.current_it_title = selected_it_title
                                                st.session_state.current_it_id = it_id
                                                st.session_state.n_attempts = n_attempts # Mantém o número de tentativas do backend
                                                st.rerun()
                        else: st.error("Erro ao carregar ITs.")
                    except Exception as e: st.error(f"Erro: {e}")
                
                if "current_quiz" in st.session_state and st.session_state.current_quiz:
                    # Segurança Extra: Verifica se o usuário (mesmo admin) pode realmente fazer este quiz
                    it_id_check = st.session_state.get("current_it_id")
                    if it_id_check:
                        n_att, approved = get_attempts_count(it_id_check, headers)
                        if approved or n_att >= 2:
                            st.error("🚫 Você já concluiu este treinamento ou atingiu o limite de tentativas individuais.")
                            if st.button("⬅️ Voltar para Seleção"):
                                st.session_state.current_quiz = None
                                st.rerun()
                            st.stop()

                    if st.button("⬅️ Voltar"):
                        st.session_state.current_quiz = None
                        st.rerun()
                    st.markdown(f"### 📝 Quiz: {st.session_state.get('current_it_title', 'Capacitação')}")
                    q_list = st.session_state.current_quiz.get("questoes", st.session_state.current_quiz.get("questions", []))
                    user_answers = {}
                    for i, q in enumerate(q_list):
                        st.markdown(f"**{i + 1}. {q['pergunta']}**")
                        st.caption(f"📍 Pilar: {q.get('pilar', 'Operação')}")
                        user_answers[q["pergunta"]] = st.radio("Sua resposta:", q["opcoes"], key=f"q_{i}")
                    
                    if st.button("✅ Finalizar"):
                        score = 0
                        # MAPEADOR DE PILARES CIRÚRGICO (EXPANDIDO)
                        pillar_map = {
                            "Segurança": "Comportamento Seguro", "Comportamento Seguro": "Comportamento Seguro", "Safe": "Comportamento Seguro",
                            "Meio Ambiente": "Consciência Ambiental", "Consciência Ambiental": "Consciência Ambiental", "Ambiental": "Consciência Ambiental",
                            "ABS": "ABS e RH", "RH": "ABS e RH", "ABS & RH": "ABS e RH", "ABS e RH": "ABS e RH", "Gestão": "ABS e RH", "Sistemas de Gestão": "ABS e RH", "Recursos Humanos": "ABS e RH", "Gente": "ABS e RH", "Sistemas": "ABS e RH", "Gestao": "ABS e RH", "Pessoas": "ABS e RH",
                            "Processo": "Processo e Qualidade", "Qualidade": "Processo e Qualidade", "Processo e Qualidade": "Processo e Qualidade",
                            "Manutenção": "Manutenção", "Operação": "Operação"
                        }
                        official_pillars = ["Comportamento Seguro", "Consciência Ambiental", "ABS e RH", "Processo e Qualidade", "Manutenção", "Operação"]
                        p_score = {p: 0 for p in official_pillars}
                        p_total = {p: 0 for p in official_pillars}

                        for q in q_list:
                            # Traduz o pilar da IA para o oficial com busca semântica
                            pilar_ia = q.get('pilar', 'Operação')
                            pk = "Operação" # Default
                            
                            # Busca por palavra-chave para garantir ABS e RH
                            pilar_ia_lower = pilar_ia.lower()
                            if any(word in pilar_ia_lower for word in ["gestão", "gestao", "rh", "abs", "gente", "pessoas", "recursos", "sistemas"]):
                                pk = "ABS e RH"
                            else:
                                pk = pillar_map.get(pilar_ia, "Operação")
                                
                            p_total[pk] = p_total.get(pk, 0) + 1
                            if user_answers[q['pergunta']] == q['resposta_correta']:
                                score += 1
                                p_score[pk] = p_score.get(pk, 0) + 1
                        
                        f_score = (score / len(q_list)) * 10 if len(q_list) > 0 else 0
                        st.session_state.last_training_score = f_score
                        st.session_state.last_training_pillars = {p: (p_score[p] / p_total[p]) * 10 if p_total.get(p, 0) > 0 else 0 for p in p_score}
                        

                        it_id_to_submit = st.session_state.get("current_it_id")
                        if not it_id_to_submit:
                            # Tenta recuperar do quiz se não estiver no session_state
                            it_id_to_submit = st.session_state.current_quiz.get("it_id")
                        
                        submit_response = requests.post(f"{API_URL}/performance/submit-result", json={"it_id": it_id_to_submit, "score": f_score, "pillars": st.session_state.last_training_pillars}, headers=headers)
                        if submit_response.status_code != 200:
                            st.error(f"Erro ao salvar resultado do quiz: {submit_response.status_code} - {submit_response.json().get('detail', 'Erro desconhecido')}")
                            # Se houver erro ao salvar, não devemos prosseguir como se o quiz tivesse sido concluído com sucesso
                            st.session_state.quiz_completed = False
                            st.session_state.current_quiz = None
                            st.rerun() # Recarrega para que o usuário possa tentar novamente ou ver o erro
                        
                        # Armazena os resultados para exibição
                        st.session_state.quiz_completed = True
                        st.session_state.last_quiz_score = f_score
                        st.session_state.last_quiz_pillars = st.session_state.last_training_pillars
                        st.session_state.last_quiz_it_title = st.session_state.get("current_it_title", "Capacitação")
                        st.session_state.last_quiz_it_id = it_id_to_submit
                        st.session_state.current_quiz = None # Limpa o quiz atual para que um novo possa ser carregado se o usuário voltar

                        # n_att é o número de tentativas ANTES desta. Para o feedback, precisamos do número atual.
                        # O número de tentativas já é atualizado pelo backend, então usamos o valor retornado por get_attempts_count
                        # após a submissão do resultado.
                        current_n_att, _ = get_attempts_count(it_id_to_submit, headers)

                        st.session_state.quiz_results_to_display = {
                            "score": f_score,
                            "pillars": st.session_state.last_training_pillars,
                            "it_title": st.session_state.get("current_it_title", "Capacitação"),
                            "it_id": it_id_to_submit,
                            "n_attempts": current_n_att,
                            "q_list": q_list,
                            "user_answers": user_answers
                        }
                        st.rerun() # Força o recarregamento para exibir a tela de resultados



                elif st.session_state.get("quiz_completed", False):
                    results = st.session_state.quiz_results_to_display
                    f_score = results["score"]
                    current_n_att = results["n_attempts"]
                    q_list = results["q_list"]
                    user_answers = results["user_answers"]
                    it_title = results["it_title"]

                    st.markdown(f"### ✅ Quiz Finalizado: {it_title}")
                    st.markdown(f"### Resultado: {f_score:.2f}/10")
                    st.info("💡 **Metodologia Alumar/ITO:** Pilares com nota abaixo de 7.0 são zerados no cálculo ponderado.")

                    if f_score >= 7.0:
                        st.success("🎉 Aprovado!")
                        # Usa o nome completo se disponível, senão usa o username
                        user_full_name = st.session_state.get("full_name") or st.session_state.get("username", "Operador")
                        
                        # Extrai pilares com nota >= 7.0
                        pillars_data = results.get("pillars", {})
                        approved_pillars = [p for p, s in pillars_data.items() if s >= 7.0]
                        
                        cert = gerar_certificado_pdf(user_full_name, it_title, f_score, approved_pillars=approved_pillars)
                        st.download_button("📄 Baixar Certificado", cert, "certificado.pdf", "application/pdf")
                    else:
                        # Se current_n_att for uma tupla (erro anterior), pegamos apenas o primeiro valor
                        n_val = current_n_att[0] if isinstance(current_n_att, tuple) else current_n_att
                        st.error(f"❌ Reprovado ({n_val}/2)")
                        if n_val >= 2:
                            st.warning("🚫 Limite de tentativas atingido para este treinamento.")

                    st.markdown("---")
                    st.markdown("#### 🔍 Revisão do Desempenho:")
                    for i, q in enumerate(q_list):
                        is_correct = user_answers[q['pergunta']] == q['resposta_correta']
                        if is_correct:
                            st.success(f"✅ Questão {i+1}: Correta!")
                        else:
                            st.error(f"❌ Questão {i+1}: Incorreta.")
                            # Feedback Inteligente: Só mostra a resposta se for aprovado ou se for a última tentativa
                            n_val = current_n_att[0] if isinstance(current_n_att, tuple) else current_n_att
                            if f_score >= 7.0 or n_val >= 2:
                                st.info(f"**Resposta correta:** {q['resposta_correta']}")
                            # A justificativa (conceito) sempre aparece para ajudar no aprendizado
                            if "justificativa" in q:
                                st.write(f"*Justificativa Técnica:* {q['justificativa']}")

                    if f_score < 7.0:
                        n_val = current_n_att[0] if isinstance(current_n_att, tuple) else current_n_att
                        if n_val == 1:
                            st.warning("💡 Estude as justificativas acima e tente novamente. Esta foi sua 1ª tentativa.")
                        elif n_val >= 2:
                            st.error("🚫 Limite de tentativas atingido. Procure seu instrutor para reciclagem.")
                            st.button("⬅️ Voltar para a Lista de ITs", disabled=True, key="btn_voltar_disabled")

                    if st.button("⬅️ Voltar para a Lista de ITs", key="btn_voltar_ativo"):
                        st.session_state.current_it_id = None
                        st.session_state.current_it_title = None
                        st.session_state.current_quiz = None
                        if "n_attempts" in st.session_state: del st.session_state.n_attempts # Remove para que seja buscado novamente
                        st.session_state.quiz_completed = False # Reseta o estado de quiz concluído
                        st.session_state.quiz_results_to_display = None # Limpa os resultados exibidos
                        st.rerun()

            with tab_matrix:
                st.subheader("📈 Matriz de Versatilidade")
                try:
                    matrix_res = requests.get(f"{API_URL}/performance/skills-matrix", headers=headers)
                    if matrix_res.status_code == 200:
                        matrix_data = matrix_res.json()
                        if matrix_data:
                            rows = []
                            # Pega o ID do usuário logado para uma filtragem 100% segura
                            user_id_logged = st.session_state.get("user_id")
                            
                            for entry in matrix_data:
                                op_name = entry.get("operator_name", "Desconhecido")
                                it_title = entry.get("it_title", "Treinamento")
                                user_id_entry = entry.get("user_id")
                                
                                # FILTRO DE PRIVACIDADE CIRÚRGICO (POR ID)
                                if not is_admin:
                                    if str(user_id_entry).strip() != str(user_id_logged).strip():
                                        continue
                                
                                p = entry.get("pillar_scores", {})
                                matrix_pillars = ["Comportamento Seguro", "Consciência Ambiental", "ABS e RH", "Processo e Qualidade", "Manutenção", "Operação"]
                                row_data = {"Operador": op_name, "Treinamento (IT)": it_title}
                                for pillar in matrix_pillars:
                                    score = float(p.get(pillar, 0.0))
                                    status = "Apto" if score >= 8.0 else "Pendente" # Regra Alumar: 8.0 para aprovação no pilar
                                    color = 'green' if status == 'Apto' else 'red'
                                    row_data[pillar] = f"<span style='color: {color};'>{score:.1f} ({status})</span>"
                                rows.append(row_data)
                            
                            if rows:
                                st.markdown(pd.DataFrame(rows).to_html(escape=False), unsafe_allow_html=True)
                            else:
                                st.info("Nenhum resultado disponível para exibição.")

                        else:
                            st.info("Nenhum resultado registrado na matriz ainda.")
                    else:
                        st.error("Erro ao carregar matriz de versatilidade.")
                except Exception as e:
                    st.error(f"Erro na matriz: {e}")


        render_performance_module(API_URL, get_headers())

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
