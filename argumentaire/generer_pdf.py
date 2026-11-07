# -*- coding: utf-8 -*-
"""Génère l'argumentaire PDF « Gagner sans frapper ».

Usage : python3 argumentaire/generer_pdf.py
Sortie : argumentaire/gagner-sans-frapper.pdf
"""
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
    TableStyle, PageBreak, KeepTogether, Flowable,
)
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Circle, Polygon
from reportlab.graphics import renderPDF

# ---------------------------------------------------------------- polices
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("Sans", os.path.join(FONT_DIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("Sans-Bold", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Serif-Bold", os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("Sans", normal="Sans", bold="Sans-Bold", italic="Sans", boldItalic="Sans-Bold")

# ---------------------------------------------------------------- couleurs
INK = colors.HexColor("#0b0b0b")
INK2 = colors.HexColor("#52514e")
MUTED = colors.HexColor("#8a8984")
GRID = colors.HexColor("#e4e3df")
SOFT = colors.HexColor("#f4f3f0")
BLUE = colors.HexColor("#2a78d6")      # mobilisation de masse / non-violence
BLUE_SOFT = colors.HexColor("#e6effa")
ORANGE = colors.HexColor("#eb6834")    # violence
ORANGE_SOFT = colors.HexColor("#fdeee7")
GRAY = colors.HexColor("#9a9993")      # contexte politique / institutionnel
WHITE = colors.white

PAGE_W, PAGE_H = A4
MARGIN = 18 * mm
CONTENT_W = PAGE_W - 2 * MARGIN

# ---------------------------------------------------------------- styles
def S(name, **kw):
    base = dict(fontName="Sans", fontSize=9.6, leading=14, textColor=INK, alignment=TA_LEFT)
    base.update(kw)
    return ParagraphStyle(name, **base)

body = S("body", spaceAfter=6)
body_small = S("small", fontSize=8.2, leading=11.5, textColor=INK2)
h1 = S("h1", fontName="Serif-Bold", fontSize=20, leading=25, spaceBefore=4, spaceAfter=8)
h2 = S("h2", fontName="Sans-Bold", fontSize=12, leading=16, spaceBefore=10, spaceAfter=5)
kicker = S("kicker", fontName="Sans-Bold", fontSize=8, leading=10, textColor=BLUE, spaceAfter=2)
caption = S("caption", fontSize=7.6, leading=10, textColor=INK2, spaceBefore=3, spaceAfter=8)
bullet = S("bullet", leftIndent=12, bulletIndent=2, spaceAfter=3)
cell = S("cell", fontSize=7.8, leading=10.2)
cell_b = S("cellb", fontName="Sans-Bold", fontSize=7.8, leading=10.2)
cell_h = S("cellh", fontName="Sans-Bold", fontSize=7.8, leading=10.2, textColor=WHITE)
quote = S("quote", fontName="Serif-Bold", fontSize=13, leading=18, textColor=INK, alignment=TA_LEFT)


def P(text, style=body):
    return Paragraph(text, style)


def bullets(items, style=bullet):
    return [Paragraph(t, style, bulletText="•") for t in items]


class DrawingFlowable(Flowable):
    def __init__(self, drawing):
        super().__init__()
        self.d = drawing
        self.width, self.height = drawing.width, drawing.height

    def wrap(self, aw, ah):
        return self.width, self.height

    def draw(self):
        renderPDF.draw(self.d, self.canv, 0, 0)


def box(flowables, bg=SOFT, border=None, pad=9, width=CONTENT_W):
    t = Table([[flowables]], colWidths=[width])
    st = [
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LEFTPADDING", (0, 0), (-1, -1), pad),
        ("RIGHTPADDING", (0, 0), (-1, -1), pad),
        ("TOPPADDING", (0, 0), (-1, -1), pad),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad),
    ]
    if border is not None:
        st.append(("LINEBEFORE", (0, 0), (0, -1), 3, border))
    t.setStyle(TableStyle(st))
    return t


def stat_tiles(tiles, accent=BLUE, num_size=19):
    """tiles = [(chiffre, libellé), ...]"""
    n = len(tiles)
    gap = 4 * mm
    w = (CONTENT_W - gap * (n - 1)) / n
    num_style = S("num", fontName="Serif-Bold", fontSize=num_size, leading=num_size + 3, textColor=INK)
    lab_style = S("lab", fontSize=7.6, leading=10, textColor=INK2)
    cells = []
    for num, lab in tiles:
        inner = Table([[Paragraph(num, num_style)], [Paragraph(lab, lab_style)]], colWidths=[w - 14])
        inner.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ]))
        cells.append(inner)
    row, widths = [], []
    for i, c in enumerate(cells):
        row.append(c)
        widths.append(w)
        if i < n - 1:
            row.append("")
            widths.append(gap)
    t = Table([row], colWidths=widths)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]
    for i in range(0, len(row), 2):
        st += [("BACKGROUND", (i, 0), (i, 0), SOFT),
               ("LINEABOVE", (i, 0), (i, 0), 2.5, accent),
               ("LEFTPADDING", (i, 0), (i, 0), 7), ("RIGHTPADDING", (i, 0), (i, 0), 7)]
    t.setStyle(TableStyle(st))
    return t


# ---------------------------------------------------------------- graphiques
def chart_chenoweth():
    W, H = CONTENT_W, 40 * mm
    d = Drawing(W, H)
    left = 62 * mm
    right = W - 14 * mm
    plot_w = right - left
    bars = [
        ("Campagnes non violentes", 53, BLUE),
        ("Campagnes violentes", 26, ORANGE),
    ]
    d.add(String(0, H - 10, "Taux de réussite des grandes campagnes de contestation, 1900-2006",
                 fontName="Sans-Bold", fontSize=9, fillColor=INK))
    d.add(String(0, H - 22, "323 campagnes dans le monde, part ayant atteint leur objectif (%)",
                 fontName="Sans", fontSize=7.5, fillColor=INK2))
    base_y = 18
    # grille
    for v in (0, 25, 50, 75, 100):
        x = left + plot_w * v / 100
        d.add(Line(x, base_y - 2, x, base_y + 62, strokeColor=GRID, strokeWidth=0.6))
        d.add(String(x, base_y - 11, f"{v} %", fontName="Sans", fontSize=6.8,
                     fillColor=MUTED, textAnchor="middle"))
    bar_h = 18
    for i, (lab, val, col) in enumerate(bars):
        y = base_y + 8 + (1 - i) * 30
        d.add(Rect(left, y, plot_w * val / 100, bar_h, fillColor=col, strokeColor=None, rx=2, ry=2))
        d.add(String(left - 6, y + 6, lab, fontName="Sans", fontSize=8.2, fillColor=INK, textAnchor="end"))
        d.add(String(left + plot_w * val / 100 + 5, y + 5.5, f"{val} %", fontName="Sans-Bold",
                     fontSize=10, fillColor=INK))
    d.add(Line(left, base_y - 2, left, base_y + 62, strokeColor=INK2, strokeWidth=0.8))
    return d


def chart_wasow():
    W, H = CONTENT_W, 40 * mm
    d = Drawing(W, H)
    d.add(String(0, H - 10, "Effet des manifestations sur le vote : États-Unis, années 1960",
                 fontName="Sans-Bold", fontSize=9, fillColor=INK))
    d.add(String(0, H - 22, "Variation du vote démocrate des électeurs blancs à proximité des protestations "
                 "(points de %, fourchette estimée)", fontName="Sans", fontSize=7.5, fillColor=INK2))
    left = 62 * mm
    right = W - 10 * mm
    vmin, vmax = -6, 4
    def X(v):
        return left + (v - vmin) / (vmax - vmin) * (right - left)
    base_y = 12
    top = base_y + 70
    for v in range(vmin, vmax + 1, 2):
        d.add(Line(X(v), base_y, X(v), top, strokeColor=GRID, strokeWidth=0.6))
        lab = f"+{v}" if v > 0 else f"{v}"
        d.add(String(X(v), base_y - 10, lab, fontName="Sans", fontSize=6.8, fillColor=MUTED, textAnchor="middle"))
    d.add(Line(X(0), base_y, X(0), top, strokeColor=INK2, strokeWidth=0.9))
    rows = [
        ("Manifestations non violentes", 1.6, 2.5, BLUE, "+1,6 à +2,5"),
        ("Émeutes, violences", -5.4, -2.2, ORANGE, "−2,2 à −5,4"),
    ]
    for i, (lab, a, b, col, txt) in enumerate(rows):
        y = base_y + 8 + (1 - i) * 30
        # barre pleine jusqu'à la borne basse, puis fourchette hachurée/claire
        lo, hi = (a, b)
        near = lo if lo > 0 else hi       # borne la plus proche de 0
        far = hi if lo > 0 else lo
        x0, x1 = sorted([X(0), X(near)])
        d.add(Rect(x0, y, x1 - x0, 18, fillColor=col, strokeColor=None, rx=2, ry=2))
        x0, x1 = sorted([X(near), X(far)])
        light = BLUE_SOFT if col == BLUE else ORANGE_SOFT
        d.add(Rect(x0, y, x1 - x0, 18, fillColor=light, strokeColor=col, strokeWidth=0.8, rx=2, ry=2))
        d.add(String(left - 6, y + 6, lab, fontName="Sans", fontSize=8.2, fillColor=INK, textAnchor="end"))
        tx = X(far) + 5 if far > 0 else X(far) - 5
        anchor = "start" if far > 0 else "end"
        if far < 0:
            # place l'étiquette à droite du zéro pour ne pas déborder à gauche
            tx, anchor = X(0) + 5, "start"
        d.add(String(tx, y + 5.5, txt, fontName="Sans-Bold", fontSize=9, fillColor=INK, textAnchor=anchor))
    return d


TIMELINE = [
    # (année, libellé ligne 1, ligne 2, catégorie, échec ?)
    (1848, "Suffrage univ. masculin,", "abolition de l'esclavage", "V", False),
    (1864, "Droit de grève", "(fin du délit de coalition)", "M", False),
    (1871, "Commune de Paris", "écrasée dans le sang", "V", True),
    (1884, "Liberté syndicale", "(loi Waldeck-Rousseau)", "I", False),
    (1906, "Repos hebdomadaire", "(après Courrières)", "M", False),
    (1919, "Journée de 8 heures", "(après-guerre)", "I", False),
    (1936, "Congés payés, 40 h,", "conventions collectives", "M", False),
    (1945, "Sécurité sociale", "(Libération, CNR)", "I", False),
    (1968, "Grenelle : SMIG +35 %,", "droit syndical", "M", False),
    (1975, "Droit à l'IVG", "(loi Veil)", "M", False),
    (1986, "Retrait de la", "loi Devaquet", "M", False),
    (1995, "Recul partiel", "du plan Juppé", "M", False),
    (2006, "Retrait du CPE", "", "M", False),
    (2018, "Gilets jaunes :", "≈ 10 Md€ de mesures", "V", False),
    (2023, "Retraites : réforme", "adoptée malgré tout", "M", True),
    (2026, "Lycéens : fin de", "Parcoursup annoncée", "M", False),
]
CAT_COLOR = {"M": BLUE, "V": ORANGE, "I": GRAY}


def chart_timeline():
    W = CONTENT_W
    row_h = 46 * mm
    H = 2 * row_h + 18 * mm
    d = Drawing(W, H)
    d.add(String(0, H - 10, "Comment les grands acquis ont été obtenus (1848-2026)",
                 fontName="Sans-Bold", fontSize=9, fillColor=INK))
    # légende
    lx = 0
    ly = H - 24
    for col, lab, hollow in [(BLUE, "Mobilisation de masse, surtout pacifique", False),
                             (ORANGE, "Violence importante", False),
                             (GRAY, "Contexte politique / institutionnel", False),
                             (INK2, "Échec ou défaite", True)]:
        if hollow:
            d.add(Circle(lx + 4, ly + 3, 3.6, fillColor=WHITE, strokeColor=INK2, strokeWidth=1.4))
        else:
            d.add(Circle(lx + 4, ly + 3, 4, fillColor=col, strokeColor=None))
        d.add(String(lx + 11, ly, lab, fontName="Sans", fontSize=7.2, fillColor=INK2))
        lx += 11 + pdfmetrics.stringWidth(lab, "Sans", 7.2) + 12
    items = TIMELINE
    per_row = 8
    for r in range(2):
        chunk = items[r * per_row:(r + 1) * per_row]
        y_axis = H - 30 * mm - r * row_h - 8
        x_start, x_end = 8, W - 8
        d.add(Line(x_start, y_axis, x_end, y_axis, strokeColor=INK2, strokeWidth=1))
        step = (x_end - x_start) / per_row
        for i, (yr, l1, l2, cat, fail) in enumerate(chunk):
            x = x_start + step * (i + 0.5)
            col = CAT_COLOR[cat]
            above = (i % 2 == 0)
            stem = 14 if above else -14
            d.add(Line(x, y_axis, x, y_axis + stem, strokeColor=GRID, strokeWidth=0.8))
            if fail:
                d.add(Circle(x, y_axis, 4.8, fillColor=WHITE, strokeColor=col, strokeWidth=2))
            else:
                d.add(Circle(x, y_axis, 5.2, fillColor=col, strokeColor=WHITE, strokeWidth=1.5))
            if above:
                ty = y_axis + stem + 22
            else:
                ty = y_axis + stem - 10
            d.add(String(x, ty, str(yr), fontName="Sans-Bold", fontSize=8.5, fillColor=INK, textAnchor="middle"))
            d.add(String(x, ty - 10, l1, fontName="Sans", fontSize=6.6, fillColor=INK2, textAnchor="middle"))
            if l2:
                d.add(String(x, ty - 18.5, l2, fontName="Sans", fontSize=6.6, fillColor=INK2, textAnchor="middle"))
    return d


def chart_opinion():
    W, H = CONTENT_W, 40 * mm
    d = Drawing(W, H)
    d.add(String(0, H - 10, "Le mouvement de 2026 dans l'opinion",
                 fontName="Sans-Bold", fontSize=9, fillColor=INK))
    d.add(String(0, H - 22, "Part des personnes interrogées (%) — Elabe, 6-7 oct. 2026 ; enquête Cepremap-HEC, oct. 2026",
                 fontName="Sans", fontSize=7.5, fillColor=INK2))
    left = 70 * mm
    right = W - 14 * mm
    pw = right - left
    rows = [
        ("Lycéens qui soutiennent le mouvement", 92),
        ("Français qui approuvent la mobilisation", 55),
        ("Français qui la soutiennent activement", 26),
    ]
    base_y = 14
    for v in (0, 25, 50, 75, 100):
        x = left + pw * v / 100
        d.add(Line(x, base_y, x, base_y + 3 * 24, strokeColor=GRID, strokeWidth=0.6))
        d.add(String(x, base_y - 10, f"{v} %", fontName="Sans", fontSize=6.8, fillColor=MUTED, textAnchor="middle"))
    for i, (lab, v) in enumerate(rows):
        y = base_y + 4 + (2 - i) * 24
        d.add(Rect(left, y, pw * v / 100, 15, fillColor=BLUE, strokeColor=None, rx=2, ry=2))
        d.add(String(left - 6, y + 4.5, lab, fontName="Sans", fontSize=8, fillColor=INK, textAnchor="end"))
        d.add(String(left + pw * v / 100 + 5, y + 4, f"{v} %", fontName="Sans-Bold", fontSize=9.5, fillColor=INK))
    d.add(Line(left, base_y, left, base_y + 74, strokeColor=INK2, strokeWidth=0.8))
    return d


def _arrow(d, x1, y1, x2, y2, col):
    d.add(Line(x1, y1, x2, y2, strokeColor=col, strokeWidth=1.4))
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    s = 5
    p1 = (x2 - s * math.cos(ang - 0.45), y2 - s * math.sin(ang - 0.45))
    p2 = (x2 - s * math.cos(ang + 0.45), y2 - s * math.sin(ang + 0.45))
    d.add(Polygon([x2, y2, p1[0], p1[1], p2[0], p2[1]], fillColor=col, strokeColor=None))


def chart_cycles():
    W, H = CONTENT_W, 74 * mm
    d = Drawing(W, H)
    half = W / 2
    def cycle(ox, title, steps, col, soft):
        d.add(String(ox + half / 2 - 4, H - 10, title, fontName="Sans-Bold", fontSize=9,
                     fillColor=INK, textAnchor="middle"))
        bw, bh = 34 * mm, 14 * mm
        cx, cy = ox + half / 2 - 4, (H - 16) / 2
        rx, ry = 23 * mm, 20 * mm
        pos = [(cx, cy + ry), (cx + rx, cy), (cx, cy - ry), (cx - rx, cy)]
        for (px, py), (l1, l2) in zip(pos, steps):
            d.add(Rect(px - bw / 2, py - bh / 2, bw, bh, fillColor=soft, strokeColor=col, strokeWidth=1, rx=4, ry=4))
            d.add(String(px, py + 1.5, l1, fontName="Sans-Bold", fontSize=7.4, fillColor=INK, textAnchor="middle"))
            d.add(String(px, py - 8, l2, fontName="Sans", fontSize=6.8, fillColor=INK2, textAnchor="middle"))
        # flèches entre les boîtes (sens horaire)
        g = 2
        _arrow(d, pos[0][0] + bw / 2 + g, pos[0][1] - 4, pos[1][0] - 6, pos[1][1] + bh / 2 + g, col)
        _arrow(d, pos[1][0] - 6, pos[1][1] - bh / 2 - g, pos[2][0] + bw / 2 + g, pos[2][1] + 4, col)
        _arrow(d, pos[2][0] - bw / 2 - g, pos[2][1] + 4, pos[3][0] + 6, pos[3][1] - bh / 2 - g, col)
        _arrow(d, pos[3][0] + 6, pos[3][1] + bh / 2 + g, pos[0][0] - bw / 2 - g, pos[0][1] - 4, col)
    cycle(0, "Le cercle vicieux", [
        ("Violence contre", "des personnes"),
        ("Répression,", "lois sécuritaires"),
        ("Blessés, colère,", "radicalisation"),
        ("Opinion qui se", "détourne"),
    ], ORANGE, ORANGE_SOFT)
    cycle(half + 4, "Le cercle vertueux", [
        ("Mobilisation", "massive et unie"),
        ("Soutien de", "l'opinion"),
        ("Pression politique", "et économique"),
        ("Concessions,", "nouveaux droits"),
    ], BLUE, BLUE_SOFT)
    d.add(Line(half, 6, half, H - 20, strokeColor=GRID, strokeWidth=0.8))
    return d


# ---------------------------------------------------------------- tableaux
def history_table():
    head = ["Mouvement", "Ampleur", "Violence ?", "Résultat", "Ce qu'on en retient"]
    rows = [
        ["1848 – Révolution de février", "Insurrection parisienne", "Oui, barricades",
         "Suffrage universel masculin, abolition de l'esclavage",
         "La violence a ouvert la porte… et l'a refermée en juin 1848 (milliers de morts)."],
        ["1871 – Commune de Paris", "Paris insurgé", "Oui, guerre civile",
         "Écrasée : 7 000 à 20 000 morts selon les estimations",
         "L'affrontement armé a mené à la défaite et à la répression."],
        ["1936 – Front populaire", "≈ 2 millions de grévistes, occupations d'usines",
         "Très peu", "Congés payés, 40 h, conventions collectives, salaires +7 à 15 %",
         "Le nombre et la grève, appuyés par une victoire électorale."],
        ["Mai 1968", "≈ 7 millions de grévistes", "Oui côté étudiants (barricades)",
         "Grenelle : SMIG +35 %, salaires +10 %, section syndicale",
         "Les gains viennent de la grève générale ; le désordre a aussi nourri le raz-de-marée gaulliste de juin."],
        ["1986 – Loi Devaquet", "Centaines de milliers d'étudiants", "Faible ; mort de Malik Oussekine (violence policière)",
         "Loi retirée", "Mouvement pacifique ; la mort d'un étudiant a choqué le pays."],
        ["1995 – Plan Juppé", "3 semaines de grève des transports", "Faible",
         "Recul sur les régimes spéciaux (en partie)", "La grève bloque l'économie sans blesser personne."],
        ["2006 – CPE", "Jusqu'à 1 à 3 millions de manifestants", "Marginale (casseurs isolés)",
         "CPE retiré", "Unité étudiants-syndicats + opinion favorable."],
        ["2016 – Loi Travail", "14 journées", "Affrontements fréquents",
         "Loi adoptée (49.3)", "La violence n'a pas fait reculer le gouvernement."],
        ["2018-19 – Gilets jaunes", "Mouvement diffus, très populaire au début",
         "Forte (Arc de Triomphe, blessés des deux côtés)", "≈ 10 Md€ de mesures, taxe carburant annulée",
         "Contre-exemple sérieux, mais coût humain lourd et loi « anticasseurs »."],
        ["2023 – Retraites", "1,28 M (police) à 3,5 M (CGT) le 7 mars",
         "Faible, puis tensions après le 49.3", "Réforme adoptée ; suspendue fin 2025 par compromis parlementaire",
         "Ni le nombre seul ni la colère n'ont suffi face au 49.3."],
        ["2026 – Lycéens et vie chère", "Plus de 1 000 lycées touchés, jusqu'à 550 000-800 000 manifestants",
         "Oui, en marge (pillages, incendies)", "Fin de Parcoursup annoncée, 15 000 places en plus, rénovations",
         "Gains partiels obtenus par la masse ; la violence a « éclipsé » les revendications."],
    ]
    data = [[Paragraph(h, cell_h) for h in head]]
    for r in rows:
        data.append([Paragraph(r[0], cell_b)] + [Paragraph(c, cell) for c in r[1:]])
    widths = [30 * mm, 31 * mm, 28 * mm, 39 * mm, CONTENT_W - 128 * mm]
    t = Table(data, colWidths=widths, repeatRows=1)
    st = [
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, GRID),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            st.append(("BACKGROUND", (0, i), (-1, i), SOFT))
    t.setStyle(TableStyle(st))
    return t


def objections_table():
    rows = [
        ("« Sans violence, on n'a jamais rien obtenu. »",
         "Faux dans les faits : congés payés (1936), retrait du CPE (2006), IVG (1975) ou retrait de la loi Devaquet (1986) "
         "ont été obtenus sans violence contre les personnes. Ce qui revient à chaque fois : le <b>nombre</b>, la <b>grève</b> "
         "et le <b>soutien de l'opinion</b>."),
        ("« Les Gilets jaunes ont obtenu 10 milliards grâce à la casse. »",
         "La casse a sans doute pesé, mais le mouvement avait alors 70 % d'opinions favorables. Ensuite, le soutien a reculé, "
         "le gouvernement a durci la loi (2019) et le bilan humain a été lourd : environ 2 500 manifestants et 1 800 membres "
         "des forces de l'ordre blessés, plus de vingt personnes éborgnées."),
        ("« La révolution de 1789 ou 1848, c'était violent. »",
         "C'est vrai, et il faut le reconnaître. Mais ces révolutions ont aussi produit la Terreur, les journées de juin 1848 "
         "et le Second Empire. Dans une démocratie qui permet de voter, de faire grève et de manifester, ce qui fait gagner a changé."),
        ("« La non-violence, c'est être gentil et ne rien bloquer. »",
         "Non : grève, blocage d'un lycée, occupation, boycott, désobéissance civile sont des actions <b>non violentes</b> et "
         "très contraignantes. La non-violence n'est pas la passivité, c'est le refus de blesser."),
        ("« La police est violente, on ne fait que se défendre. »",
         "Les violences policières sont réelles et documentées (FIDH, 2026). Justement : un cortège pacifique rend ces violences "
         "visibles et indéfendables. Quand des manifestants frappent aussi, le débat se déplace vers « l'ordre public »."),
        ("« La non-violence a échoué en 2023. »",
         "Oui, elle ne garantit rien. Mais la violence non plus (2016). L'échec de 2023 vient surtout du 49.3 et de l'absence "
         "de débouché politique : il faut donc ajouter la grève reconductible et le vote, pas des coups."),
    ]
    data = [[Paragraph("Ce qu'on entend", cell_h), Paragraph("Ce qu'on peut répondre", cell_h)]]
    for a, b in rows:
        data.append([Paragraph(a, cell_b), Paragraph(b, cell)])
    t = Table(data, colWidths=[48 * mm, CONTENT_W - 48 * mm], repeatRows=1)
    st = [
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, GRID),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            st.append(("BACKGROUND", (0, i), (-1, i), SOFT))
    t.setStyle(TableStyle(st))
    return t


# ---------------------------------------------------------------- page
def on_page(canv, doc):
    canv.saveState()
    canv.setFont("Sans", 7)
    canv.setFillColor(MUTED)
    canv.drawString(MARGIN, 10 * mm, "Gagner sans frapper — argumentaire, novembre 2026")
    canv.drawRightString(PAGE_W - MARGIN, 10 * mm, str(doc.page))
    canv.setStrokeColor(GRID)
    canv.setLineWidth(0.5)
    canv.line(MARGIN, 13 * mm, PAGE_W - MARGIN, 13 * mm)
    canv.restoreState()


def on_cover(canv, doc):
    canv.saveState()
    canv.setFillColor(INK)
    canv.rect(0, PAGE_H - 92 * mm, PAGE_W, 92 * mm, stroke=0, fill=1)
    canv.setFillColor(BLUE)
    canv.rect(0, PAGE_H - 92 * mm, PAGE_W, 2.2 * mm, stroke=0, fill=1)
    canv.setFillColor(colors.HexColor("#9fc3ef"))
    canv.setFont("Sans-Bold", 9)
    canv.drawString(MARGIN, PAGE_H - 26 * mm, "ARGUMENTAIRE · NOVEMBRE 2026")
    canv.setFillColor(WHITE)
    canv.setFont("Serif-Bold", 34)
    canv.drawString(MARGIN, PAGE_H - 44 * mm, "Gagner sans frapper")
    canv.setFont("Sans", 12)
    canv.setFillColor(colors.HexColor("#d9d8d3"))
    canv.drawString(MARGIN, PAGE_H - 56 * mm, "Acquis sociaux, mobilisations et violence en France :")
    canv.drawString(MARGIN, PAGE_H - 62.5 * mm, "ce que montrent l'histoire, la recherche et l'actualité.")
    canv.setFont("Sans", 8.5)
    canv.setFillColor(colors.HexColor("#a9a8a2"))
    canv.drawString(MARGIN, PAGE_H - 78 * mm,
                    "1848 · 1936 · 1968 · 2006 · Gilets jaunes · Retraites 2023 · Mouvement lycéen 2026")
    canv.restoreState()
    on_page(canv, doc)


# ---------------------------------------------------------------- contenu
def build(path):
    doc = BaseDocTemplate(path, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=MARGIN, bottomMargin=18 * mm,
                          title="Gagner sans frapper",
                          author="Argumentaire",
                          subject="Acquis sociaux, mobilisations et violence en France")
    frame_cover = Frame(MARGIN, 18 * mm, CONTENT_W, PAGE_H - 92 * mm - 18 * mm - 8 * mm, id="cover",
                        leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    frame = Frame(MARGIN, 18 * mm, CONTENT_W, PAGE_H - MARGIN - 18 * mm, id="main",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[frame_cover], onPage=on_cover),
        PageTemplate(id="Main", frames=[frame], onPage=on_page),
    ])
    from reportlab.platypus import NextPageTemplate
    s = []

    # ---------------- Page 1 : la thèse
    s.append(NextPageTemplate("Main"))
    s.append(P("LA THÈSE EN UNE PHRASE", kicker))
    s.append(box([P("Les acquis sociaux se gagnent par <b>le nombre, l'unité, la grève et le soutien de l'opinion</b>. "
                    "La violence contre les personnes n'est ni nécessaire ni efficace : elle divise, elle justifie la "
                    "répression et elle fait oublier les revendications.", quote)], bg=BLUE_SOFT, border=BLUE, pad=12))
    s.append(Spacer(1, 10))
    s.append(stat_tiles([
        ("53 % vs 26 %", "taux de réussite des campagnes non violentes vs violentes dans le monde (1900-2006)"),
        ("3,5 %", "de la population mobilisée : seuil au-delà duquel presque aucune campagne n'a échoué (≈ 2,4 millions en France)"),
        ("1936", "congés payés et 40 h obtenus par des grèves avec occupation, quasiment sans violence"),
    ]))
    s.append(Spacer(1, 10))
    s.append(P("Ce que ce document défend", h2))
    s += bullets([
        "<b>On peut obtenir des droits sans frapper.</b> Une bonne partie des grandes conquêtes sociales françaises "
        "du XX<super>e</super> siècle vient de grèves et de manifestations de masse.",
        "<b>Il faut être honnête avec l'histoire.</b> Certaines avancées sont nées dans la violence (1848) ou dans un "
        "contexte de guerre (Sécurité sociale, 1945). Le document le dit, et explique pourquoi cela ne prouve pas que la violence soit la méthode.",
        "<b>La ligne rouge, ce sont les personnes.</b> Blesser un policier, un manifestant, un passant ou un employé, c'est "
        "franchir une limite morale et c'est aussi perdre stratégiquement.",
        "<b>La casse matérielle est un débat à part.</b> Elle n'a pas le même poids moral, mais elle a aussi un coût "
        "pour le mouvement (voir page 6).",
    ])
    s.append(Spacer(1, 4))
    s.append(P("Pourquoi en parler maintenant ?", h2))
    s.append(P("Depuis la mi-septembre 2026, un mouvement lycéen et étudiant inédit, rejoint par la contestation contre la vie "
               "chère et l'intersyndicale, secoue la France. La plupart des rassemblements sont calmes, mais certaines journées "
               "(17 octobre) ont tourné aux pillages et aux affrontements, avec des blessés des deux côtés. D'où la question : "
               "faut-il la violence pour gagner ?"))

    s.append(PageBreak())

    # ---------------- Page 2 : la recherche
    s.append(P("1 · CE QUE DIT LA RECHERCHE", kicker))
    s.append(P("La non-violence n'est pas naïve : c'est souvent la méthode qui marche le mieux", h1))
    s.append(P("Les politologues Erica Chenoweth et Maria Stephan ont étudié 323 grandes campagnes de contestation dans le monde "
               "entre 1900 et 2006. Résultat : les campagnes non violentes ont réussi <b>deux fois plus souvent</b> que les campagnes "
               "violentes. La raison principale : elles attirent beaucoup plus de monde (jeunes, personnes âgées, salariés, familles), "
               "et c'est le nombre qui fait plier un pouvoir."))
    s.append(DrawingFlowable(chart_chenoweth()))
    s.append(P("Source : E. Chenoweth et M. Stephan, <i>Why Civil Resistance Works</i>, Columbia University Press, 2011. "
               "Attention : ces campagnes visaient surtout des changements de régime ou l'indépendance, pas des réformes sociales ; "
               "et depuis 2010 les taux de réussite ont baissé pour les deux types, l'écart en faveur de la non-violence restant net.",
               caption))
    s.append(P("La violence fait basculer l'opinion… dans le mauvais sens", h2))
    s.append(P("Le chercheur Omar Wasow (Princeton) a mesuré l'effet des manifestations des années 1960 aux États-Unis sur le vote. "
               "Près des manifestations pacifiques pour les droits civiques, le vote pour le camp favorable aux réformes "
               "<b>augmente</b>. Près des émeutes, il <b>baisse</b> nettement, au point, selon l'auteur, d'avoir pu faire élire "
               "Richard Nixon en 1968 sur le thème de « la loi et l'ordre »."))
    s.append(DrawingFlowable(chart_wasow()))
    s.append(P("Source : O. Wasow, « Agenda Seeding », <i>American Political Science Review</i>, 2020. Partie foncée : effet minimal "
               "estimé ; partie claire : fourchette haute.", caption))
    s.append(box([P("<b>Le « dilemme de l'activiste ».</b> Des psychologues de Stanford et Toronto (Feinberg, Willer et Kovacheff, 2020) "
                    "ont montré par des expériences que les actions perçues comme extrêmes, y compris la casse, font baisser le soutien "
                    "au mouvement : le public s'identifie moins à lui, même s'il partage ses idées. Nuance : d'autres travaux montrent "
                    "qu'une aile radicale peut parfois faire paraître les modérés plus raisonnables, et donc les renforcer.", body_small)],
                 bg=SOFT, border=GRAY))

    s.append(PageBreak())

    # ---------------- Page 3 : l'histoire
    s.append(P("2 · L'HISTOIRE DE FRANCE, HONNÊTEMENT", kicker))
    s.append(P("Les droits sociaux sont surtout nés de la grève et du nombre", h1))
    s.append(P("Regarder l'histoire sans l'arranger, c'est admettre que tout n'a pas été obtenu dans le calme. La République et le "
               "suffrage universel sont nés de révolutions. Mais une fois la démocratie installée, la plupart des grandes conquêtes "
               "sociales ont été arrachées par des <b>grèves massives</b>, des <b>manifestations</b> et des <b>victoires électorales</b>. "
               "Et quand l'affrontement armé a pris le dessus, comme en 1871, il a mené au massacre."))
    s.append(DrawingFlowable(chart_timeline()))
    s.append(P("Frise non proportionnelle. Classement simplifié : chaque acquis a des causes multiples (rapport de force, élections, "
               "contexte international). « Violence importante » signifie que la violence a joué un rôle central dans l'épisode.",
               caption))
    s.append(P("Trois moments clés", h2))
    s.append(P("<b>1936 – Le modèle.</b> Après la victoire électorale du Front populaire, près de deux millions de salariés font grève "
               "et occupent leurs usines, souvent dans une ambiance de fête. Aucune émeute : la pression vient de l'arrêt de la production. "
               "En quelques jours, les accords de Matignon et les lois de juin donnent les congés payés (deux semaines), la semaine de "
               "40 heures, les conventions collectives et des hausses de salaires de 7 à 15 %."))
    s.append(P("<b>Mai 1968 – La leçon à double tranchant.</b> Les barricades étudiantes ont fait la une, mais ce sont les sept millions "
               "de grévistes qui ont obtenu les accords de Grenelle (SMIG +35 %, salaires +10 %, droit syndical dans l'entreprise). "
               "Et le désordre a aussi effrayé une partie du pays : en juin 1968, les gaullistes remportent une majorité écrasante."))
    s.append(P("<b>Gilets jaunes – Le contre-exemple qu'il faut prendre au sérieux.</b> Après les violences du 1<super>er</super> "
               "décembre 2018, le gouvernement lâche environ 10 milliards d'euros de mesures. La casse a donc pu peser. Mais le mouvement "
               "avait aussi un soutien populaire massif, et la suite a été lourde : des milliers de blessés des deux côtés, des personnes "
               "mutilées, un soutien qui s'effrite, et une loi « anticasseurs » qui restreint le droit de manifester pour tout le monde."))

    s.append(PageBreak())

    # ---------------- Page 4 : tableau
    s.append(P("2 · L'HISTOIRE DE FRANCE, HONNÊTEMENT (SUITE)", kicker))
    s.append(P("Onze mouvements passés au crible", h1))
    s.append(P("Le tableau montre que <b>la violence n'est pas le point commun des victoires</b>. Le point commun, c'est l'ampleur de "
               "la mobilisation, la capacité à bloquer l'économie (grève) et le soutien de la population. À l'inverse, des mouvements "
               "violents (1871, 2016) ont échoué, et un mouvement pacifique (2023) aussi : la non-violence est une condition, pas une garantie."))
    s.append(history_table())
    s.append(P("Chiffres arrondis, issus des bilans officiels et syndicaux (souvent très différents) et des travaux d'historiens.",
               caption))

    s.append(PageBreak())

    # ---------------- Page 5 : actualité
    s.append(P("3 · CE QUE MONTRE L'ACTUALITÉ (AUTOMNE 2026)", kicker))
    s.append(P("Le mouvement de 2026 : la masse obtient, la violence brouille", h1))
    s.append(P("Parti de blocages de lycées en Île-de-France à la mi-septembre, le mouvement s'est étendu à plus de "
               "1 000 établissements dès le 1<super>er</super> octobre. Les revendications sont concrètes : bâtiments vétustes, "
               "professeurs absents non remplacés, emplois du temps trop lourds, Parcoursup, moyens pour l'éducation."))
    s.append(stat_tiles([
        ("450 000", "manifestants le 6 octobre selon les syndicats (250 000 selon le ministère)"),
        ("550 000+", "manifestants le 17 octobre (550 000 à 800 000), jour de « convergence des colères »"),
        ("≈ 6 600", "interpellations au 7 octobre, dont 87 % de mineurs (FIDH)"),
        ("997", "policiers et gendarmes blessés le 17 octobre, dont 7 gravement (ministère)"),
    ], num_size=16))
    s.append(Spacer(1, 10))
    s.append(DrawingFlowable(chart_opinion()))
    s.append(P("Une majorité de Français approuve la mobilisation, mais seuls 26 % la soutiennent vraiment : c'est en dessous de la "
               "moyenne des mouvements mesurés par Elabe depuis 2017 (60 % d'approbation). Les images de violences pèsent sur ce chiffre.",
               caption))
    s.append(P("Ce que le mouvement a déjà obtenu", h2))
    s += bullets([
        "Annonce du <b>remplacement de Parcoursup</b> par un nouveau système ;",
        "<b>15 000 places supplémentaires</b> dans l'enseignement supérieur ;",
        "Des <b>prêts avantageux aux régions</b> pour rénover les lycées ;",
        "La <b>suspension des grenades assourdissantes</b> pendant le mouvement.",
    ])
    s.append(P("Ces gains sont partiels (les syndicats lycéens les jugent insuffisants), mais ils viennent de la <b>pression du nombre</b> : "
               "des centaines de lycées bloqués, des cortèges massifs, une jeunesse soutenue à 92 % par les siens."))
    s.append(P("Ce que la violence a coûté", h2))
    s += bullets([
        "<b>Le message a disparu.</b> Après le 17 octobre, le journal de TF1 se demandait « pourquoi les violences ont éclipsé les "
        "revendications ». On a parlé du boulevard Haussmann en feu, plus des lycées qui tombent en ruine.",
        "<b>Le gouvernement a changé de récit.</b> Le Premier ministre parle désormais de « violences urbaines » et un projet de loi "
        "« casseurs-payeurs » est en préparation : la question sociale devient une question d'ordre public.",
        "<b>Des jeunes en paient le prix.</b> Des milliers de mineurs en garde à vue, des blessés, des familles inquiètes : "
        "autant de personnes qui risquent de quitter le mouvement.",
    ])

    s.append(PageBreak())

    # ---------------- Page 6 : la casse
    s.append(P("4 · ET LA CASSE MATÉRIELLE ?", kicker))
    s.append(P("Une vitrine n'est pas une personne… mais la casse a un prix", h1))
    s.append(P("Il y a une vraie différence morale entre briser la vitrine d'une banque et frapper un être humain. Beaucoup de "
               "militants la font, et ce document la reconnaît. Mais si l'objectif est de <b>gagner</b>, il faut regarder ce que la casse "
               "produit concrètement."))
    t = Table([[
        [P("<b>Les arguments de ceux qui la défendent</b>", S("x", fontName="Sans-Bold", fontSize=9.5, leading=13)),
         Spacer(1, 4)] + bullets([
            "Elle vise des symboles (banques, multinationales), pas des personnes.",
            "Elle attire l'attention des médias et du pouvoir.",
            "Une aile radicale peut faire passer les modérés pour des interlocuteurs « raisonnables ».",
            "Des épisodes historiques (1848, Gilets jaunes) montrent que le désordre peut faire céder un gouvernement.",
        ], S("b1", fontSize=8.4, leading=11.5, leftIndent=10, bulletIndent=0, spaceAfter=3)),
        [P("<b>Ce qu'il faut savoir avant de la défendre</b>", S("y", fontName="Sans-Bold", fontSize=9.5, leading=13)),
         Spacer(1, 4)] + bullets([
            "Les expériences montrent que la casse fait baisser le soutien du public, même chez ceux qui partagent les idées.",
            "Elle met des personnes en danger : un incendie se propage, des gens vivent et travaillent au-dessus des agences.",
            "Elle est punie par la loi et sert à justifier des lois restreignant le droit de manifester (2019, 2026).",
            "Elle se confond facilement avec le pillage de petits commerces ou de voitures de particuliers.",
            "Elle décourage les familles, les salariés et les plus âgés de venir : le nombre baisse.",
        ], S("b2", fontSize=8.4, leading=11.5, leftIndent=10, bulletIndent=0, spaceAfter=3)),
    ]], colWidths=[CONTENT_W / 2 - 3, CONTENT_W / 2 - 3], spaceBefore=4)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (0, 0), SOFT), ("BACKGROUND", (1, 0), (1, 0), ORANGE_SOFT),
        ("LINEABOVE", (0, 0), (0, 0), 2.5, GRAY), ("LINEABOVE", (1, 0), (1, 0), 2.5, ORANGE),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    s.append(t)
    s.append(Spacer(1, 10))
    s.append(P("Des actions qui frappent fort sans casser", h2))
    s.append(P("Viser les banques et les grands groupes, c'est possible sans casse, et souvent plus efficace pour l'image du mouvement :"))
    s += bullets([
        "<b>Grève et grève reconductible</b> : c'est ce qui a fait plier le patronat en 1936 et en 1968 ;",
        "<b>Boycott</b> d'enseignes, <b>changement de banque</b> collectif, campagnes de désinvestissement ;",
        "<b>Occupations pacifiques</b> de halls d'agences ou de sièges sociaux, sit-in, chaînes humaines ;",
        "<b>Actions symboliques</b> (banderoles géantes, faux billets, « die-in ») qui font des images fortes sans victimes ;",
        "<b>Blocages filtrants</b> de lycées, de dépôts ou de ronds-points, comme au début des Gilets jaunes.",
    ])
    s.append(Spacer(1, 6))
    s.append(box([P("<b>En résumé :</b> on peut comprendre la colère contre les symboles du capitalisme. Mais la casse n'a jamais été "
                    "ce qui a fait gagner un mouvement en France ; au mieux elle a accompagné une mobilisation massive, au pire elle l'a "
                    "affaiblie. Et contre les personnes, aucune justification ne tient.", body)], bg=BLUE_SOFT, border=BLUE))

    s.append(PageBreak())

    # ---------------- Page 7 : objections + cycles
    s.append(P("5 · RÉPONDRE AUX OBJECTIONS", kicker))
    s.append(P("« Sans violence, on n'obtient rien » : six réponses", h1))
    s.append(objections_table())
    s.append(Spacer(1, 12))
    s.append(KeepTogether([
        P("« La violence n'engendre que la violence »", h2),
        DrawingFlowable(chart_cycles()),
        P("Chaque violence contre une personne relance un cycle qui profite au pouvoir ; la mobilisation de masse relance un cycle "
          "qui profite au mouvement.", caption),
    ]))

    s.append(PageBreak())

    # ---------------- Page 8 : conclusion
    s.append(P("6 · CE QUI FAIT VRAIMENT GAGNER", kicker))
    s.append(P("Les cinq leviers d'un mouvement victorieux", h1))
    levers = [
        ("1. Le nombre", "Plus on est nombreux et divers (lycéens, salariés, retraités, familles), plus le pouvoir doit céder. "
                         "Le seuil des 3,5 % de la population, c'est environ 2,4 millions de personnes en France."),
        ("2. La grève", "C'est l'arme qui a obtenu les congés payés et le SMIG +35 %. Elle coûte cher à l'économie sans blesser personne."),
        ("3. L'unité", "En 2006, étudiants et syndicats unis ont fait tomber le CPE. Un mouvement divisé entre « pacifistes » "
                       "et « casseurs » est plus facile à discréditer."),
        ("4. L'opinion", "Un mouvement populaire protège ses manifestants et met le gouvernement sous pression. La violence est le moyen "
                         "le plus rapide de perdre ce soutien."),
        ("5. Un débouché politique", "1936 et 1981 montrent que les urnes transforment une mobilisation en lois. 2023 montre qu'un "
                                     "mouvement sans débouché peut perdre malgré des millions de manifestants."),
    ]
    rows = [[Paragraph(a, S("la", fontName="Sans-Bold", fontSize=10, leading=13, textColor=BLUE)),
             Paragraph(b, body)] for a, b in levers]
    lt = Table(rows, colWidths=[44 * mm, CONTENT_W - 44 * mm])
    lt.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, GRID),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    s.append(lt)
    s.append(Spacer(1, 12))
    s.append(box([
        P("CONCLUSION", S("k2", fontName="Sans-Bold", fontSize=8, leading=10, textColor=colors.HexColor("#9fc3ef"))),
        Spacer(1, 3),
        P("L'histoire de France ne dit pas que tout s'est fait dans le calme. Elle dit que, dans une démocratie, les grandes "
          "conquêtes sociales viennent d'abord de <b>gens nombreux, unis et déterminés</b> qui arrêtent le travail, descendent dans la "
          "rue et gagnent l'opinion. Être radical dans ses revendications et ferme dans ses moyens d'action, oui. Frapper des personnes, "
          "non : c'est injuste, et c'est offrir au pouvoir la meilleure raison de ne pas écouter.",
          S("cc", fontSize=10.5, leading=15.5, textColor=WHITE)),
    ], bg=INK, pad=14))
    s.append(Spacer(1, 14))
    s.append(P("Sources principales", h2))
    src = [
        "E. Chenoweth, M. Stephan, <i>Why Civil Resistance Works</i>, Columbia University Press, 2011 ; E. Chenoweth, "
        "<i>Civil Resistance: What Everyone Needs to Know</i>, Oxford University Press, 2021.",
        "O. Wasow, « Agenda Seeding: How 1960s Black Protests Moved Elites, Public Opinion and Voting », "
        "<i>American Political Science Review</i>, 2020.",
        "M. Feinberg, R. Willer, C. Kovacheff, « The activist's dilemma », <i>Journal of Personality and Social Psychology</i>, 2020 ; "
        "B. Simpson, R. Willer, M. Feinberg, « Radical flanks of social movements can increase support for moderate factions », "
        "<i>PNAS Nexus</i>, 2022.",
        "Histoire sociale : M. Margairaz et D. Tartakowsky, <i>Le Front populaire</i> ; M. Zancarini-Fournel, "
        "<i>Les luttes et les rêves</i> (2016) ; bilans officiels des mouvements de 1995, 2006, 2016, 2018-19 et 2023.",
        "Mouvement de 2026 : franceinfo (revendications et réponse du gouvernement) ; Public Sénat (mesures annoncées) ; "
        "Maire-info ; FIDH, « France : violente répression du mouvement lycéen » ; Le Grand Continent (sondage Elabe, 6-7 oct.) ; "
        "Cepremap-HEC Paris (enquête jeunes) ; ministère de l'Intérieur (bilans des 17 et 31 octobre) ; Paris Match, "
        "Economie Matin, Politis, TF1 (journal du 18 oct.).",
    ]
    s += bullets(src, S("src", fontSize=7.6, leading=10.4, textColor=INK2, leftIndent=10, bulletIndent=0, spaceAfter=2))
    s.append(Spacer(1, 4))
    s.append(P("Les chiffres de 2026 évoluent vite et diffèrent selon les sources (police, syndicats, ONG). Ils sont arrêtés au "
               "7 novembre 2026.", caption))

    doc.build(s)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gagner-sans-frapper.pdf")
    build(out)
    print(out)
