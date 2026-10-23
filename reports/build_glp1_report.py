from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import sys

OUT = sys.argv[1]
INK = colors.HexColor("#1b2a35")
TEAL = colors.HexColor("#0f6e74")
LIGHT = colors.HexColor("#e7f2f2")
GREY = colors.HexColor("#5b6770")
LINE = colors.HexColor("#c9d3d6")
W = 6.9 * inch

H1 = ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=TEAL, spaceBefore=4, spaceAfter=6)
B = ParagraphStyle("B", fontName="Helvetica", fontSize=10.2, leading=14.5, textColor=INK, spaceAfter=6)
BUL = ParagraphStyle("BUL", parent=B, leftIndent=14, bulletIndent=3, spaceAfter=4)
CELL = ParagraphStyle("C", parent=B, fontSize=9, leading=12, spaceAfter=0)
CELLH = ParagraphStyle("CH", parent=CELL, fontName="Helvetica-Bold", textColor=colors.white)
SMALL = ParagraphStyle("S", parent=B, fontSize=7.8, leading=10.2, textColor=GREY, spaceAfter=2)
BIG = ParagraphStyle("BIG", parent=B, fontName="Helvetica-Bold", fontSize=20, leading=23, textColor=TEAL, spaceAfter=0)
BIGL = ParagraphStyle("BIGL", parent=B, fontSize=8.6, leading=11, textColor=GREY, spaceAfter=0)


def p(t, s=B):
    return Paragraph(t, s)


def bullets(items):
    return [Paragraph(i, BUL, bulletText="•") for i in items]


def table(rows, widths):
    data = [[Paragraph(c, CELLH if r == 0 else CELL) for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), 0.4, LINE),
          ("BACKGROUND", (0, 0), (-1, 0), TEAL),
          ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]
    st += [("BACKGROUND", (0, r), (-1, r), colors.HexColor("#f4f8f8")) for r in range(2, len(rows), 2)]
    t.setStyle(TableStyle(st))
    return t


def callout(text):
    t = Table([[Paragraph(text, B)]], colWidths=[W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT), ("LINEBEFORE", (0, 0), (0, -1), 3, TEAL),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                           ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    return t


def stats(items):
    cells = [[Paragraph(v, BIG), Paragraph(l, BIGL)] for v, l in items]
    t = Table([[Table([[a], [b]]) for a, b in cells]], colWidths=[W / len(items)] * len(items))
    t.setStyle(TableStyle([("LINEABOVE", (0, 0), (-1, 0), 1.5, TEAL), ("TOPPADDING", (0, 0), (-1, -1), 6),
                           ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    return t


def first_page(c, doc):
    c.saveState()
    c.setFillColor(TEAL)
    c.rect(0, 9.35 * inch, 8.5 * inch, 1.65 * inch, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 9)
    c.drawString(0.8 * inch, 10.6 * inch, "FOR THE PRINCIPALS OF myLAB BOX  ·  OCTOBER 2026")
    c.setFont("Helvetica-Bold", 24)
    c.drawString(0.8 * inch, 10.1 * inch, "GLP-1 Testing: Our Next Big Market")
    c.setFont("Helvetica", 11.5)
    c.drawString(0.8 * inch, 9.7 * inch, "We built at-home testing. This is the category where that head start pays off most.")
    c.restoreState()
    footer(c, doc)


def footer(c, doc):
    c.saveState()
    c.setFont("Helvetica", 7.5)
    c.setFillColor(GREY)
    c.drawString(0.8 * inch, 0.5 * inch, "GLP-1 Testing: Our Next Big Market  ·  myLAB Box internal")
    c.drawRightString(7.7 * inch, 0.5 * inch, f"{doc.page}")
    c.restoreState()


s = []
s.append(Spacer(1, 1.35 * inch))
s.append(stats([("1 in 8", "U.S. adults say they take a GLP-1 drug today (KFF, 2025)"),
                ("4–6", "blood panels per patient over two years of treatment"),
                ("$250M", "Quest’s consumer testing sales in 2025, up 20%+")]))
s.append(Spacer(1, 12))
s.append(p("The opportunity", H1))
s.append(p("Millions of Americans now take Wegovy, Zepbound, Ozempic or similar drugs. Safe treatment calls for blood work "
           "before the first dose, again around month three, then every 6 to 12 months. That turns each patient into a "
           "<b>repeat customer</b> for testing, no matter which drug or pharmacy they use."))
s.append(p("Many of these patients get their care online, through telehealth. They need labs that come to them. "
           "That is the business myLAB Box helped create: we were among the first to offer at-home lab screening, starting in 2013, and have grown into a broad at-home testing brand."))
s.append(callout("<b>The ask:</b> make GLP-1 testing a funded priority, with a dedicated owner, its own budget and clear 12-month targets. "
                 "The market is moving now. Competitors launched GLP-1 panels this year, and the winners will be decided in the next 12 to 18 months."))
s.append(Spacer(1, 6))

s.append(p("Why act now", H1))
s += bullets([
    "<b>The big labs are in.</b> Labcorp and Quest both sell GLP-1 baseline and follow-up panels. Quest’s direct-to-consumer site grew ~35% in 2025.",
    "<b>Newcomers launched in 2026.</b> Noom (17 markers, $125), SiPhox (40+ markers, $199), Choose Health and Everlywell ($134) all released GLP-1 panels this year.",
    "<b>Investors are paying for testing tied to care.</b> Nourish raised $100M and Altro Health raised $7M to pair GLP-1 treatment with lab testing.",
    "<b>Platforms need a lab partner.</b> Ro earned an estimated $370M from GLP-1 care in 2024. Noom uses an outside partner (Ash) for its at-home GLP-1 testing. These deals go to whoever is ready first.",
])
s.append(PageBreak())

s.append(p("Where we stand", H1))
s.append(table([
    ["", "myLAB Box today", "What winners offer"],
    ["Panel", "At-Home GLP-1 Test, $159: thyroid, lipids, kidney, liver", "Adds HbA1c, B12, vitamin D, iron, inflammation (Noom: 17 markers at $125)"],
    ["Repeat testing", "One-time kit", "Subscription that follows the treatment schedule"],
    ["Clinical follow-up", "Results delivered to the customer", "Clinician review when a result is abnormal"],
    ["Partners", "Mostly direct-to-consumer", "White-label kits inside telehealth and clinic programs"],
    ["Reliability", "Public reviews cite slow shipping and support (Trustpilot ~2/5)", "Tracked kits, results in about a week"],
], [1.25 * inch, 2.65 * inch, 3.0 * inch]))
s.append(Spacer(1, 8))
s.append(p("Our advantages are real: a known brand, more than a decade of at-home testing, CLIA/CAP-certified partner labs, "
           "a GLP-1 product already on the market, and years of test results that newer companies do not have. "
           "What we lack is depth, repeat business and partners. Those are fixable with focus and funding."))

s.append(p("What it takes to win market share", H1))
s += bullets([
    "<b>1. Fix delivery first.</b> Tracked shipping both ways, results within 7 days, faster support. A GLP-1 patient on a 3-month schedule will not reorder after a lost kit, and partners read reviews.",
    "<b>2. Build the best GLP-1 panel.</b> Add HbA1c, B12, vitamin D, ferritin, lipase and hs-CRP. Offer a Baseline kit and a Follow-up kit, priced near Noom and Everlywell.",
    "<b>3. Sell a schedule, not a kit.</b> A subscription that ships the next test at month 3, 6 and 12. HSA/FSA eligible.",
    "<b>4. Add a clinician step.</b> Abnormal results go to a clinician review. This makes our test part of care, which is what partners and insurers pay for.",
    "<b>5. Go where the patients are.</b> White-label kits and an ordering link for GLP-1 telehealth companies, clinics, gyms and medspas. Target two signed partners in 12 months.",
])

s.append(p("What it could be worth", H1))
s.append(table([
    ["Active GLP-1 customers", "Year-one sales (4 tests × $159)", "Share of ~10M U.S. patients"],
    ["2,500", "$1.6M", "0.025%"],
    ["10,000", "$6.4M", "0.1%"],
    ["25,000 (with partner deals)", "$15.9M", "0.25%"],
], [2.3 * inch, 2.3 * inch, 2.3 * inch]))
s.append(Spacer(1, 4))
s.append(p("Planning estimates at today’s price. Customers who stay on treatment keep buying in year two (about 2 tests a year).", SMALL))
s.append(Spacer(1, 6))
s.append(callout("<b>One tenth of one percent</b> of U.S. GLP-1 patients is a ~$6M first-year line for myLAB Box. "
                 "We created at-home testing. We should lead its biggest new market."))
s.append(PageBreak())

s.append(p("Sources and notes", H1))
s.append(p("Every figure was checked against public sources in October 2026. Several numbers in the original research notes "
           "were wrong or could not be confirmed and were left out (for example: “38 million Americans”, a $149 myLAB Box price, "
           "a 2025 Medicare CGM expansion, and several market-size forecasts).", SMALL))
src = [
    "KFF poll, 12% of U.S. adults currently taking a GLP-1 (Nov 2025). kff.org",
    "J.P. Morgan Research: ~10M Americans on GLP-1 treatment in 2025, 25–30M by 2030. jpmorgan.com/insights/global-research",
    "Testing schedule: clinical lab guidance (Australian Clinical Labs, Sept 2026; LabFinder, Nov 2025).",
    "Quest: ~$250M consumer-initiated testing in 2025, 20%+ growth; questhealth.com +35%. Quest Q4 2025 earnings; 360Dx.",
    "Labcorp Weight Loss Management portfolio (Mar 2024). labcorp.com",
    "Noom biomarker kit, 17 markers, $125 (May 2026). Fierce Healthcare.",
    "SiPhox GLP Monitoring Panel, 40+ markers, $199 at launch. ycombinator.com/launches",
    "Choose Health GLP-1 panels (Apr 2026); Everlywell Metabolic & GLP-1 panel, $134. everlywell.com",
    "Nourish $100M Series C (May 2026), Fierce Healthcare; Altro Health $7M seed (Oct 2026), Fitt Insider.",
    "Ro GLP-1 revenue ~$370M in 2024 (Sacra estimate); Ash–Noom GLP-1 testing partnership (Business Wire, Dec 2025).",
    "myLAB Box At-Home GLP-1 Test, $159, not available in NY (mylabbox.com); founded 2013 (CB Insights); Trustpilot rating ~2/5.",
    "Revenue figures on page 2 are internal planning estimates, not forecasts.",
]
for i, t in enumerate(src, 1):
    s.append(p(f"{i}. {t}", SMALL))

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                        topMargin=0.7 * inch, bottomMargin=0.75 * inch,
                        title="GLP-1 Testing: Our Next Big Market", author="myLAB Box internal")
doc.build(s, onFirstPage=first_page, onLaterPages=footer)
print("ok")
