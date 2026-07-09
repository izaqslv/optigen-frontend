import tempfile
from datetime import datetime
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image as RLImage)
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from core.config import UNIDADES


# ===============================
# INTERPRETAÇÃO
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