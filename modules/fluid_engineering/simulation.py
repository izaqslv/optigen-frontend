import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from core.config import BASE_URL
from core.auth import get_headers

def run_simulation():
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
                    f"{BASE_URL}/fluid-engineering/analyze",
                    json=payload,
                    headers=get_headers(),
                    timeout=120
                )
            except Exception as e:
                st.error(f"Erro de conexão: {e}")
                st.stop()

            if response.status_code != 200:
                st.error("Erro no backend (/fluid-engineering/analyze)")
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
                    f"{BASE_URL}/fluid-engineering/simulate",
                    json=payload,
                    headers=get_headers(),
                    timeout=120
                )
            except Exception as e:
                st.error(f"Erro ao chamar simulate: {e}")
                st.stop()

            if resp_sim.status_code != 200:
                st.error("Erro no backend (/fluid-engineering/simulate)")
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
