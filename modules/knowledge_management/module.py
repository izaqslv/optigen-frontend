import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from services.pdf.certificate_service import gerar_certificado_pdf

def run_knowledge_management(API_URL, headers):
    def get_attempts_count(it_id, headers):
        try:
            response = requests.get(f"{API_URL}/knowledge-management/my-results", headers=headers)
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
            tabs = st.tabs(
                ["📊 Dashboard ITO", "👨‍🏫 Área do Instrutor", "👷 Jornada do Operador", "📈 Matriz de Versatilidade",
                 "💬 Consultar Especialista IA"])
            tab_dash, tab_inst, tab_op, tab_matrix, tab_chat = tabs
        else:
            tabs = st.tabs(["👷 Minha Jornada", "📈 Meu Perfil de Competências", "💬 Consultar Especialista IA"])
            tab_op, tab_matrix, tab_chat = tabs

        with tab_chat:
            st.subheader("💬 Agente de IA - Consultor Técnico de Campo")
            st.markdown("Tire suas dúvidas sobre os procedimentos e normas das ITs aprovadas.")

            # Busca ITs aprovadas para o contexto do chat
            try:
                chat_its_res = requests.get(f"{API_URL}/knowledge-management/its?approved_only=True", headers=headers)
                if chat_its_res.status_code == 200:
                    chat_its = chat_its_res.json()
                    if not chat_its:
                        st.info("Aguardando ITs aprovadas para consulta.")
                    else:
                        it_chat_options = {it["title"]: it["id"] for it in chat_its}
                        selected_chat_it = st.selectbox("Sobre qual IT você deseja tirar dúvidas?",
                                                        list(it_chat_options.keys()))

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
                                    it_data_res = requests.get(
                                        f"{API_URL}/knowledge-management/it-content/{it_chat_options[selected_chat_it]}",
                                        headers=headers)
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
                                            "it_id": it_chat_options[selected_chat_it],  # Passamos o ID da IT
                                            "question": prompt
                                        }

                                        # Novo endpoint para o chat da IA
                                        ai_response = requests.post(f"{API_URL}/knowledge-management/chat-ia", json=chat_payload,
                                                                    headers=headers)

                                        if ai_response.status_code == 200:
                                            response_text = ai_response.json()["response"]
                                            st.markdown(response_text)
                                            st.session_state[chat_key].append(
                                                {"role": "assistant", "content": response_text})
                                        else:
                                            st.error(
                                                f"Erro ao consultar o especialista de IA: {ai_response.json().get('detail', 'Erro desconhecido')}")
                                    else:
                                        st.error("Não consegui acessar o manual desta IT.")

            except Exception as e:
                st.error(f"Erro no chat: {e}")

        # Definindo os 6 pilares oficiais da metodologia ITO
        all_pillars = ["Comportamento Seguro", "Consciência Ambiental", "ABS e RH", "Processo e Qualidade",
                       "Manutenção", "Operação"]

        if is_admin:
            with tab_dash:
                st.subheader("Maturidade Operacional por Pilar")
                # Busca os dados da matriz para calcular a média geral
                try:
                    matrix_res = requests.get(f"{API_URL}/knowledge-management/skills-matrix", headers=headers)
                    if matrix_res.status_code == 200:
                        matrix_data = matrix_res.json()
                        if matrix_data:
                            # Calcula a média dos scores por pilar para todos os operadores
                            pillar_averages = {p: [] for p in all_pillars}
                            for entry in matrix_data:
                                p_scores = entry.get("pillar_scores", {})
                                for pillar in all_pillars:
                                    if pillar in p_scores:  # Verifica se o pilar existe nos scores do operador
                                        pillar_averages[pillar].append(p_scores[pillar])

                            # Filtro por Operador (Busca todos os usuários cadastrados)
                            try:
                                # O endpoint correto agora existe em /users/
                                users_resp = requests.get(f"{API_URL}/users/", headers=headers)
                                if users_resp.status_code == 200:
                                    all_users_data = users_resp.json()
                                    all_operators = ["Todos os Operadores"] + sorted(
                                        list(set([u.get("username") for u in all_users_data if u.get("username")])))
                                else:
                                    # Fallback para os nomes que já estão na matriz
                                    all_operators = ["Todos os Operadores"] + sorted(list(
                                        set([entry.get("operator_name") for entry in matrix_data if
                                             entry.get("operator_name")])))
                            except:
                                all_operators = ["Todos os Operadores"] + sorted(list(
                                    set([entry.get("operator_name") for entry in matrix_data if
                                         entry.get("operator_name")])))

                            selected_op = st.selectbox("🎯 Filtrar Visão por Operador:", all_operators)

                            if selected_op != "Todos os Operadores":
                                # Filtra os dados comparando com operator_name (que é o campo que o backend retorna no skills-matrix)
                                matrix_data = [entry for entry in matrix_data if
                                               entry.get("operator_name") == selected_op]

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
                            avg_values = [sum(pillar_averages[p]) / len(pillar_averages[p]) if pillar_averages[p] else 0
                                          for p in all_pillars]

                            fig = go.Figure(data=go.Scatterpolar(r=avg_values, theta=all_pillars, fill='toself',
                                                                 name='Performance'))
                            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                                              showlegend=False, paper_bgcolor='rgba(0,0,0,0)',
                                              plot_bgcolor='rgba(0,0,0,0)', font=dict(color='grey'))
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
                    response = requests.get(f"{API_URL}/knowledge-management/its", headers=headers)
                    if response.status_code == 200:
                        available_its = response.json()
                        it_options = {it["title"]: it["id"] for it in available_its}
                        if not it_options:
                            st.warning("Nenhuma IT encontrada no banco de dados.")
                        else:
                            selected_it_title = st.selectbox("Selecione uma IT para gerar treinamento:",
                                                             list(it_options.keys()))
                            selected_it_id = it_options[selected_it_title]
                            col_btn1, col_btn2, col_btn3 = st.columns(3)
                            with col_btn1:
                                if st.button("🚀 Gerar Quiz via IA", key="generate_quiz_button",
                                             use_container_width=True):
                                    with st.spinner("🧠 Gerando Quiz..."):
                                        quiz_response = requests.post(
                                            f"{API_URL}/knowledge-management/generate-quiz/{selected_it_id}", headers=headers)
                                        if quiz_response.status_code == 200:
                                            st.success("✅ Quiz gerado!")
                                        else:
                                            st.error("Erro ao gerar quiz.")

                            with col_btn2:
                                if st.button("👁️ Visualizar IT", key="view_it_button", use_container_width=True):
                                    with st.spinner("Carregando conteúdo..."):
                                        v_res = requests.get(f"{API_URL}/knowledge-management/it-content/{selected_it_id}",
                                                             headers=headers)
                                        if v_res.status_code == 200:
                                            st.session_state.preview_it = v_res.json()["content"]
                                            st.rerun()
                                        else:
                                            st.error("Erro ao carregar IT.")

                            with col_btn3:
                                if st.button("✅ Aprovar IT", key="approve_it_button", use_container_width=True,
                                             type="primary"):
                                    with st.spinner("Sincronizando..."):
                                        appr_res = requests.post(f"{API_URL}/knowledge-management/approve-it/{selected_it_id}",
                                                                 headers=headers)
                                        if appr_res.status_code == 200:
                                            st.success(f"✅ IT '{selected_it_title}' Aprovada!")
                                            st.balloons()
                                            st.info(
                                                "Esta IT agora está disponível para os operadores na aba 'Jornada do Operador'.")
                                        else:
                                            st.error("Erro ao aprovar IT.")

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
                                        st.error("**🚨 RISCOS**\n\n" + ("\n".join(
                                            [f"- {r}" for r in riscos]) if riscos else "Nenhum risco mapeado."))
                                    with col_c:
                                        st.success("**✅ CONTROLES CRÍTICOS**\n\n" + ("\n".join([f"- {c}" for c in
                                                                                                controles]) if controles else "Nenhum controle mapeado."))
                                    with col_p:
                                        st.warning("**⚠️ CRITÉRIOS DE PARADA**\n\n" + ("\n".join(
                                            [f"- {p}" for p in parada]) if parada else "Nenhum critério de parada."))

                                    st.markdown("---")
                                    st.markdown("#### ⚙️ Fluxo de Execução")
                                    fluxo = it_prev.get('fluxo_execucao', [])
                                    if fluxo:
                                        for step in fluxo:
                                            with st.expander(
                                                    f"**Passo {step.get('passo_n', 'N/A')}: {step.get('o_que_fazer', 'N/A')}**",
                                                    expanded=True):
                                                st.markdown(f"**🛠️ Como fazer:**\n{step.get('como_fazer', 'N/A')}")
                                                st.markdown(f"**💡 Por que fazer:**\n{step.get('por_que_fazer', 'N/A')}")
                                                medidas = step.get('medidas_controle', [])
                                                if medidas:
                                                    st.caption(f"🛡️ Segurança: {', '.join(medidas)}")
                                    else:
                                        st.info("Nenhum passo de execução detalhado disponível.")

                                if st.button("Fechar Visualização", key="close_preview_bottom",
                                             use_container_width=True):
                                    st.session_state.preview_it = None
                                    st.rerun()
                    else:
                        st.error(f"Erro ao carregar ITs: {response.text}")
                except Exception as e:
                    st.error(f"Erro de conexão: {e}")

        with tab_op:
            st.subheader("👷 Minha Jornada de Conhecimento")
            if "current_quiz" not in st.session_state or st.session_state.current_quiz is None:
                st.markdown("### 📚 Selecionar Treinamento")
                try:
                    # Agora filtramos apenas ITs aprovadas para o operador
                    response = requests.get(f"{API_URL}/knowledge-management/its", params={"approved_only": "True"},
                                            headers=headers)
                    if response.status_code == 200:
                        available_its = response.json()
                        it_options = {it["title"]: it["id"] for it in available_its}
                        if not it_options:
                            st.warning("⚠️ Nenhuma IT aprovada disponível para treinamento no momento.")
                        else:
                            selected_it_title = st.selectbox("Escolha a IT para iniciar:", list(it_options.keys()),
                                                             key="op_it_select")
                            it_id = it_options[selected_it_title]

                            n_attempts, is_approved = get_attempts_count(it_id, headers)
                            if is_approved:
                                st.success("✅ Você já foi aprovado(a) nesta IT. Parabéns!")
                                st.button("🚀 Iniciar Quiz", key="op_start_quiz", disabled=True)
                            elif n_attempts >= 2:
                                st.error(
                                    f"🚫 Limite de tentativas atingido ({n_attempts}/2). Não é possível iniciar um novo quiz para esta IT.")
                                st.button("🚀 Iniciar Quiz", key="op_start_quiz", disabled=True)
                            else:
                                if n_attempts == 1: st.warning("⚠️ Última chance! Esta é sua 2ª e última tentativa.")
                                if st.button("🚀 Iniciar Quiz", key="op_start_quiz"):
                                    with st.spinner("🧠 Gerando Quiz..."):
                                        quiz_res = requests.post(f"{API_URL}/knowledge-management/generate-quiz/{it_id}",
                                                                 headers=headers)
                                        if quiz_res.status_code == 200:
                                            st.session_state.current_quiz = quiz_res.json().get("quiz", quiz_res.json())
                                            st.session_state.current_it_title = selected_it_title
                                            st.session_state.current_it_id = it_id
                                            st.session_state.n_attempts = n_attempts  # Mantém o número de tentativas do backend
                                            st.rerun()
                    else:
                        st.error("Erro ao carregar ITs.")
                except Exception as e:
                    st.error(f"Erro: {e}")

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
                q_list = st.session_state.current_quiz.get("questoes",
                                                           st.session_state.current_quiz.get("questions", []))
                user_answers = {}
                for i, q in enumerate(q_list):
                    st.markdown(f"**{i + 1}. {q['pergunta']}**")
                    st.caption(f"📍 Pilar: {q.get('pilar', 'Operação')}")
                    user_answers[q["pergunta"]] = st.radio("Sua resposta:", q["opcoes"], key=f"q_{i}")

                if st.button("✅ Finalizar"):
                    score = 0
                    # MAPEADOR DE PILARES CIRÚRGICO (EXPANDIDO)
                    pillar_map = {
                        "Segurança": "Comportamento Seguro", "Comportamento Seguro": "Comportamento Seguro",
                        "Safe": "Comportamento Seguro",
                        "Meio Ambiente": "Consciência Ambiental", "Consciência Ambiental": "Consciência Ambiental",
                        "Ambiental": "Consciência Ambiental",
                        "ABS": "ABS e RH", "RH": "ABS e RH", "ABS & RH": "ABS e RH", "ABS e RH": "ABS e RH",
                        "Gestão": "ABS e RH", "Sistemas de Gestão": "ABS e RH", "Recursos Humanos": "ABS e RH",
                        "Gente": "ABS e RH", "Sistemas": "ABS e RH", "Gestao": "ABS e RH", "Pessoas": "ABS e RH",
                        "Processo": "Processo e Qualidade", "Qualidade": "Processo e Qualidade",
                        "Processo e Qualidade": "Processo e Qualidade",
                        "Manutenção": "Manutenção", "Operação": "Operação"
                    }
                    official_pillars = ["Comportamento Seguro", "Consciência Ambiental", "ABS e RH",
                                        "Processo e Qualidade", "Manutenção", "Operação"]
                    p_score = {p: 0 for p in official_pillars}
                    p_total = {p: 0 for p in official_pillars}

                    for q in q_list:
                        # Traduz o pilar da IA para o oficial com busca semântica
                        pilar_ia = q.get('pilar', 'Operação')
                        pk = "Operação"  # Default

                        # Busca por palavra-chave para garantir ABS e RH
                        pilar_ia_lower = pilar_ia.lower()
                        if any(word in pilar_ia_lower for word in
                               ["gestão", "gestao", "rh", "abs", "gente", "pessoas", "recursos", "sistemas"]):
                            pk = "ABS e RH"
                        else:
                            pk = pillar_map.get(pilar_ia, "Operação")

                        p_total[pk] = p_total.get(pk, 0) + 1
                        if user_answers[q['pergunta']] == q['resposta_correta']:
                            score += 1
                            p_score[pk] = p_score.get(pk, 0) + 1

                    f_score = (score / len(q_list)) * 10 if len(q_list) > 0 else 0
                    st.session_state.last_training_score = f_score
                    st.session_state.last_training_pillars = {
                        p: (p_score[p] / p_total[p]) * 10 if p_total.get(p, 0) > 0 else 0 for p in p_score}

                    it_id_to_submit = st.session_state.get("current_it_id")
                    if not it_id_to_submit:
                        # Tenta recuperar do quiz se não estiver no session_state
                        it_id_to_submit = st.session_state.current_quiz.get("it_id")

                    submit_response = requests.post(f"{API_URL}/knowledge-management/submit-result",
                                                    json={"it_id": it_id_to_submit, "score": f_score,
                                                          "pillars": st.session_state.last_training_pillars},
                                                    headers=headers)
                    if submit_response.status_code != 200:
                        st.error(
                            f"Erro ao salvar resultado do quiz: {submit_response.status_code} - {submit_response.json().get('detail', 'Erro desconhecido')}")
                        # Se houver erro ao salvar, não devemos prosseguir como se o quiz tivesse sido concluído com sucesso
                        st.session_state.quiz_completed = False
                        st.session_state.current_quiz = None
                        st.rerun()  # Recarrega para que o usuário possa tentar novamente ou ver o erro

                    # Armazena os resultados para exibição
                    st.session_state.quiz_completed = True
                    st.session_state.last_quiz_score = f_score
                    st.session_state.last_quiz_pillars = st.session_state.last_training_pillars
                    st.session_state.last_quiz_it_title = st.session_state.get("current_it_title", "Capacitação")
                    st.session_state.last_quiz_it_id = it_id_to_submit
                    st.session_state.current_quiz = None  # Limpa o quiz atual para que um novo possa ser carregado se o usuário voltar

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
                    st.rerun()  # Força o recarregamento para exibir a tela de resultados

            elif st.session_state.get("quiz_completed", False):
                results = st.session_state.quiz_results_to_display
                f_score = results["score"]
                current_n_att = results["n_attempts"]
                q_list = results["q_list"]
                user_answers = results["user_answers"]
                it_title = results["it_title"]

                st.markdown(f"### ✅ Quiz Finalizado: {it_title}")
                st.markdown(f"### Resultado: {f_score:.2f}/10")
                st.info(
                    "💡 **Metodologia Alumar/ITO:** Pilares com nota abaixo de 7.0 são zerados no cálculo ponderado.")

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
                        st.success(f"✅ Questão {i + 1}: Correta!")
                    else:
                        st.error(f"❌ Questão {i + 1}: Incorreta.")
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
                    if "n_attempts" in st.session_state: del st.session_state.n_attempts  # Remove para que seja buscado novamente
                    st.session_state.quiz_completed = False  # Reseta o estado de quiz concluído
                    st.session_state.quiz_results_to_display = None  # Limpa os resultados exibidos
                    st.rerun()

        with tab_matrix:
            st.subheader("📈 Matriz de Versatilidade")
            try:
                matrix_res = requests.get(f"{API_URL}/knowledge-management/skills-matrix", headers=headers)
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
                            matrix_pillars = ["Comportamento Seguro", "Consciência Ambiental", "ABS e RH",
                                              "Processo e Qualidade", "Manutenção", "Operação"]
                            row_data = {"Operador": op_name, "Treinamento (IT)": it_title}
                            for pillar in matrix_pillars:
                                score = float(p.get(pillar, 0.0))
                                status = "Apto" if score >= 8.0 else "Pendente"  # Regra Alumar: 8.0 para aprovação no pilar
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

    render_performance_module(API_URL,headers)
