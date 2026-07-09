import os, tempfile, matplotlib.pyplot as plt
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (Image as RLImage, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle)

# ==============================
# 📄 PREMIUM SERVICES - OPTIGEN
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
    plt.imshow(pivot.values, aspect="auto", origin="lower")
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
    # 🏢 LOGOMARCA
    logo_path = "assets/logo_newgen_white.png"
    if os.path.exists(logo_path):
        content.append(RLImage(logo_path, width=140, height=110)) # width=120, height=60

    content.append(Spacer(1, 12))

    # ==============================
    # 📌 TÍTULO
    content.append(Paragraph("Relatório Técnico - OptiGen V3", styles["Title"]))
    content.append(Paragraph("Simulação e Comparação de Cenários de Sedimentação", styles["Normal"]))
    content.append(Spacer(1, 20))

    # ==============================
    # 📊 MÉTRICAS EM TABELA
    def safe_val(v):
        return "-" if v is None else str(v)

    tabela = [
        ["Métrica", "Fluido A", "Fluido B"],
        ["C topo final", f"{met_A['C_top_final']:.4f}", f"{met_B['C_top_final']:.4f}"],
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
    doc.build(content)

    return file_path, file_name
