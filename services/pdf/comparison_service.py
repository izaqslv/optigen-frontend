import tempfile
from datetime import datetime
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image as RLImage)
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from core.config import UNIDADES
from services.pdf.report_service import gerar_interpretacao


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

