# relatorio/memorial.py - Geracao do Memorial Descritivo em PDF
#
# REFERENCIAS:
#   [1] NBR 6118:2023 (apresentacao do memorial de calculo estrutural)
#   [2] REPORTLAB - biblioteca Python para geracao de PDF
import os
from datetime import datetime

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False


def _cabecalho_dados(dados):
    """Valida campos obrigatorios do dict de dados"""
    obrig = ["obra", "responsavel", "local", "data"]
    for c in obrig:
        if c not in dados:
            dados[c] = "NI"
    return dados


def gerar_memorial(resultados: dict, saida: str = "memorial.pdf", dados_obra: dict = None):
    """
    Gera memorial descritivo em PDF a partir dos resultados calculados.
    resultados: dict com chaves 'predim', 'pilares', 'vigas', 'lajes', etc.
    dados_obra: informacoes do cabecalho (obra, responsavel, local, data)
    Ref: [1] NBR 6118:2023, Anexo B (apresentacao de calculos)
    """
    if not REPORTLAB_OK:
        print("[AVISO] reportlab nao instalado. Instale com: pip install reportlab")
        _gerar_txt(resultados, saida.replace(".pdf", ".txt"), dados_obra)
        return

    if dados_obra is None:
        dados_obra = {}
    dados_obra = _cabecalho_dados(dados_obra)

    doc = SimpleDocTemplate(saida, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2.5*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    titulo  = ParagraphStyle("titulo", parent=styles["Title"],
                              fontSize=16, spaceAfter=6)
    secao   = ParagraphStyle("secao", parent=styles["Heading2"],
                              fontSize=12, spaceAfter=4, textColor=colors.darkblue)
    normal  = styles["Normal"]
    code    = ParagraphStyle("code", parent=styles["Code"],
                              fontSize=8, leading=10)

    story = []

    # Cabecalho
    story.append(Paragraph("MEMORIAL DE CALCULO ESTRUTURAL", titulo))
    story.append(Paragraph(f"NBR 6118:2023 | Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}", normal))
    story.append(Spacer(1, 0.3*cm))

    cab_data = [
        ["Obra:", dados_obra.get("obra", "—")],
        ["Responsavel:", dados_obra.get("responsavel", "—")],
        ["Local:", dados_obra.get("local", "—")],
        ["Data:", dados_obra.get("data", datetime.now().strftime("%d/%m/%Y"))],
    ]
    t = Table(cab_data, colWidths=[4*cm, 12*cm])
    t.setStyle(TableStyle([
        ("FONT", (0,0), (-1,-1), "Helvetica", 9),
        ("FONT", (0,0), (0,-1), "Helvetica-Bold", 9),
        ("BOX", (0,0), (-1,-1), 0.5, colors.grey),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.lightgrey),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#e8ecf0")),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.5*cm))

    # Normas e referencias
    story.append(Paragraph("1. NORMAS E REFERENCIAS", secao))
    refs = [
        "NBR 6118:2023 — Projeto de Estruturas de Concreto",
        "NBR 6120:2019 — Acoes para o Calculo de Estruturas de Edificacoes",
        "NBR 16868-1:2020 — Alvenaria Estrutural — Parte 1",
        "CARINI, M.R. (MSc, UFSC) — Curso Estrutural na Real, 2023",
        "BASTOS, P.S.S. (Dr., UNESP) — Apostilas CA I e CA II, 2017",
        "ARAUJO, J.M. (Dr., FURG) — Curso de Concreto Armado. v.2-4, 2014",
        "FUSCO, P.B. (Dr., USP) — Tecnica de Armar as Estruturas, 2013",
        "CAPUTO, H.P. (Dr., PUC-Rio) — Mecanica dos Solos. 7.ed, 2008",
    ]
    for r in refs:
        story.append(Paragraph(f"• {r}", normal))
    story.append(Spacer(1, 0.4*cm))

    # Materiais
    story.append(Paragraph("2. MATERIAIS ADOTADOS", secao))
    mats = resultados.get("materiais", {})
    mat_rows = [
        ["Material", "Parametro", "Valor"],
        ["Concreto", "fck", f"{mats.get('fck',25)} MPa"],
        ["", "fcd", f"{mats.get('fck',25)/1.4:.1f} MPa"],
        ["", "Ecs", f"{mats.get('Ecs',28000):.0f} MPa"],
        ["Aco CA-50", "fyk", f"{mats.get('fyk',500)} MPa"],
        ["", "fyd", f"{mats.get('fyk',500)/1.15:.0f} MPa"],
        ["", "Es", "210.000 MPa"],
        ["CAA", "Classe", mats.get("caa", "II")],
    ]
    tm = Table(mat_rows, colWidths=[4*cm, 5*cm, 7*cm])
    tm.setStyle(TableStyle([
        ("FONT", (0,0), (-1,0), "Helvetica-Bold", 9),
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#c8d8e8")),
        ("FONT", (0,1), (-1,-1), "Helvetica", 9),
        ("BOX", (0,0), (-1,-1), 0.5, colors.grey),
        ("INNERGRID", (0,0), (-1,-1), 0.25, colors.lightgrey),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f4f6f8")]),
    ]))
    story.append(tm)
    story.append(Spacer(1, 0.4*cm))

    # Secoes de calculo
    secs = {
        "predim":      ("3. PRE-DIMENSIONAMENTO", "predim"),
        "pilares":     ("4. PILARES", "pilares"),
        "vigas":       ("5. VIGAS", "vigas"),
        "lajes":       ("6. LAJES", "lajes"),
        "reservatorio":("7. RESERVATORIO", "reservatorio"),
        "muro":        ("8. MURO DE ARRIMO", "muro"),
        "piscina":     ("9. PISCINA", "piscina"),
        "viga_parede": ("10. VIGA-PAREDE", "viga_parede"),
        "portico":     ("11. ANALISE DO PORTICO (FEM 3D)", "portico"),
    }

    for chave, (titulo_sec, key) in secs.items():
        if key not in resultados:
            continue
        story.append(Paragraph(titulo_sec, secao))
        dado = resultados[key]
        if isinstance(dado, dict):
            rows = [[str(k), str(v)] for k, v in dado.items()]
            if rows:
                ts = Table(rows, colWidths=[8*cm, 8*cm])
                ts.setStyle(TableStyle([
                    ("FONT", (0,0), (-1,-1), "Helvetica", 8),
                    ("BOX", (0,0), (-1,-1), 0.3, colors.grey),
                    ("INNERGRID", (0,0), (-1,-1), 0.2, colors.lightgrey),
                    ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.white, colors.HexColor("#f6f8fa")]),
                ]))
                story.append(ts)
        elif isinstance(dado, str):
            story.append(Paragraph(dado, code))
        story.append(Spacer(1, 0.3*cm))

    # Rodape
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        "Memorial gerado automaticamente pelo Sistema de Calculo Estrutural — NBR 6118:2023.",
        normal))
    story.append(Paragraph(
        "Os resultados devem ser verificados por engenheiro responsavel.", normal))

    doc.build(story)
    print(f"[OK] Memorial gerado: {saida}")


def _gerar_txt(resultados, saida, dados_obra):
    """Fallback em TXT quando reportlab nao esta disponivel"""
    linhas = []
    linhas.append("="*60)
    linhas.append("MEMORIAL DE CALCULO ESTRUTURAL — NBR 6118:2023")
    linhas.append("="*60)
    if dados_obra:
        for k, v in dados_obra.items():
            linhas.append(f"{k}: {v}")
    linhas.append("")
    for sec, dado in resultados.items():
        linhas.append(f"\n--- {sec.upper()} ---")
        if isinstance(dado, dict):
            for k, v in dado.items():
                linhas.append(f"  {k}: {v}")
        else:
            linhas.append(str(dado))
    with open(saida, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas))
    print(f"[OK] Memorial TXT gerado: {saida}")
