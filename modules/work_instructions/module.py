import io, requests
import streamlit as st

def run_work_instructions(API_URL, headers):
    """
    Módulo Agente de Inteligência Operacional.
    """
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
                        f"{API_URL}/work-instructions/generate",
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
