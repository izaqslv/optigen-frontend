import streamlit as st, requests
from core.ui import SHOW_METADATA
from core.config import API_URL, UNIDADES
from core.auth import get_headers
from services.experimental_data_service import get_fluids
from modules.fluid_engineering.page import render_experimental_data
from modules.fluid_engineering.analysis import run_single_analysis, run_all_analysis
from modules.fluid_engineering.comparison import run_comparison
from modules.fluid_engineering.simulation import run_simulation
from modules.fluid_engineering.simulation_compare import run_simulation_compare
from modules.work_instructions.module import run_work_instructions
from modules.knowledge_management.module import run_knowledge_management
from services.pdf.report_service import gerar_pdf
from services.pdf.comparison_service import gerar_pdf_comparacao
from services.pdf.premium_service import gerar_pdf_premium

#------------------------------------------------------------
# CONTROLE GLOBAL
if "token" not in st.session_state:
    st.session_state.token = None
#------------------------------------------------------------

# CONFIG DO STREMLIT
st.set_page_config(layout="wide", page_title="OptiGen", page_icon="🔬")

#===================================================
# SEGURANÇA/USUÁRIO/SENHA DE ACESSO
#===================================================

### Tela de login
st.markdown("<br><br><br>", unsafe_allow_html=True)

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
            response = requests.post(url=f"{API_URL}/auth/login", json={"username": username,"password": password}, timeout=60)

            if response.status_code == 200:
                token = response.json()["access_token"]
                st.session_state.token = token

                # --- BUSCAR PERMISSÕES DO USUÁRIO ---
                try:
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

# ----------------------------------------------------------------------------------------------------------------------
# SISTEMA PRINCIPAL
else:
    # APP CONTINUA AQUI
    # Bloquear app sem login
    if not st.session_state.token:
        st.stop()

    st.markdown("<div style='margin-top:-140px;'>💡 Para uma melhor experiência, ative o modo escuro</div>", unsafe_allow_html=True)
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
            "</div>", unsafe_allow_html=True)

    # ------------------------------------------------------------------------------------------------------------------
    # SIDEBAR
    # 🔝 TOPO DA SIDEBAR
    st.sidebar.markdown("<div style='height:50px'></div>", unsafe_allow_html=True)
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
        """, unsafe_allow_html=True)

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

    # --- NAVEGAÇÃO DINÂMICA ---
    st.sidebar.markdown("### Menu da Plataforma OptiGen:")  # Plataforma de Simulação Inteligente:

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
        opcoes_menu.append("Gestão do Conhecimento")  # Academia ITO (Performance & Learning)

    # Renderiza o menu apenas se houver opções disponíveis
    if opcoes_menu:
        modo = st.sidebar.radio("Selecione um Módulo", opcoes_menu)
    else:
        st.sidebar.warning("⚠️ Nenhum módulo contratado.")
        st.info("Entre em contato com o suporte para ativar seus módulos.")
        st.stop()  # Interrompe a execução para não mostrar conteúdo vazio

    # ---------------------------------------
    # Estado da sessão
    # ---------------------------------------
    if "history" not in st.session_state:
        st.session_state.history = []

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
        # button {
        #     opacity: 0.2;
        # }
        # button:hover {
        #     opacity: 1;
        # }
        </style>
        """, unsafe_allow_html=True)

    # ------------------------------------------------------------------------------------------------------------------
    # MODOS (Movido para a Sidebar)
    user_modules = st.session_state.get("user_modules", [])

    # Inicializar os dados dos módulos como vazios
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

    # ------------------------------------------------------------------------------------------------------------------
    # MÓDULOS DISPONÍVEIS
    if modo == "Eng. de Fluidos (Dados Exp.)":
        (fluid_id, heights, height, generate_single, generate_all) = render_experimental_data(fluids)
        if generate_single:
            run_single_analysis(fluid_id=fluid_id, height=height, gerar_pdf=gerar_pdf, unidades=UNIDADES, show_metadata=SHOW_METADATA)
        if generate_all:
            run_all_analysis(fluid_id=fluid_id, heights=heights, unidades=UNIDADES, show_metadata=SHOW_METADATA)

    elif modo == "Eng. de Fluidos (Comparação: Dados Exp.)":
        run_comparison(fluids=fluids, gerar_pdf_comparacao=gerar_pdf_comparacao, unidades=UNIDADES, show_metadata=SHOW_METADATA)

    elif modo == "Simulação Inteligente de Fluidos":
        run_simulation()

    elif modo == "Simulação: Fluidos (A vs. B)":
        run_simulation_compare(gerar_pdf_premium=gerar_pdf_premium)

    elif modo == "Instruções de Trabalho":
        run_work_instructions(API_URL=API_URL, headers=get_headers())

    elif modo == "Gestão do Conhecimento":
        run_knowledge_management(API_URL=API_URL, headers=get_headers())

    #------------------------------RODAPÉ-------------------------------------------------------------------------------
    st.markdown("<hr style='margin-top:80px; margin-bottom:5px;'>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:right; font-size:12px; margin-top:0px;'>"
                "© 2026 NewGen Intelligent Engineering Solutions. Todos os direitos reservados."
                "</p>", unsafe_allow_html=True)