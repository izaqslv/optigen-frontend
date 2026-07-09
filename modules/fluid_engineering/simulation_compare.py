import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from core.config import BASE_URL
from core.auth import get_headers

def run_simulation_compare(gerar_pdf_premium):
    """
    Comparação Inteligente A vs. B.
    """
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
    st.markdown("### 📐 Domínio de Simulação")

    colD1, colD2, colD3 = st.columns(3)
    altura_total = colD1.number_input("Altura total (cm)", 5.0, key="cmp_altura")
    tempo_max = colD2.number_input("Tempo máximo (dia)", 10, key="cmp_tempo")
    n_alturas = colD3.number_input("Resolução", 10, key="cmp_res")

    # =======================================================================================================
    # EXECUÇÃO
    # ========================
    # 🎯 OBJETIVO DO PROCESSO
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
            resp = requests.post(f"{BASE_URL}/fluid-engineering/analyze", json=payload, headers=get_headers(), timeout=120)
            if resp.status_code != 200:
                st.error("Erro no analyze")
                st.text(resp.text)
                st.stop()
            return resp.json()["data"]

        def run_simulate(payload):
            resp = requests.post(f"{BASE_URL}/fluid-engineering/simulate", json=payload, headers=get_headers(), timeout=120)
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
        st.subheader("📈 Comparação no topo")

        dfA = pd.DataFrame(data_A.get("curva_topo", []))
        dfB = pd.DataFrame(data_B.get("curva_topo", []))

        if not dfA.empty and not dfB.empty:
            dfA = dfA.set_index("tempo")
            dfB = dfB.set_index("tempo")

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
            if score_A > score_B:
                vencedor = "A"
                st.success("🏆 Fluido A melhor desempenho global")
            else:
                vencedor = "B"
                st.success("🏆 Fluido B melhor desempenho global")

            # =========================
            # 🔍 EXPLICAÇÃO (OURO!)
            # st.markdown("### 🔍 Por que esse resultado?")
            st.markdown("### 🔍 Interpretação do Resultado")

            st.write(f"O resultado foi avaliado com foco em: **{objetivo}**")

            exp = []

            # TOPO
            if met_A["C_top_final"] < met_B["C_top_final"]:
                exp.append(
                    "🔹 Fluido A apresenta maior eficiência na redução de concentração no topo (melhor clarificação)")
            elif met_B["C_top_final"] < met_A["C_top_final"]:
                exp.append(
                    "🔹 Fluido B apresenta maior eficiência na redução de concentração no topo (melhor clarificação)")

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
        st.subheader("📊 Parecer Executivo")

        try:
            # =========================
            # 🏆 DEFINIR VENCEDOR
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
            motivos = []

            if met_v["C_top_final"] < met_p["C_top_final"]:
                motivos.append("melhor clarificação no topo")

            if met_v["C_bottom_final"] > met_p["C_bottom_final"]:
                motivos.append("maior compactação no fundo")

            if met_v["std_temporal"] < met_p["std_temporal"]:
                motivos.append("maior estabilidade ao longo do tempo")

            # =========================
            # 📢 FRASE PRINCIPAL
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