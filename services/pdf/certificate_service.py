import os, tempfile
from datetime import datetime
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image as RLImage)

# pdf DO CERTIFICADO (Certificado obtido da aprovação na Jornada de Aprendizado com as IT's)
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