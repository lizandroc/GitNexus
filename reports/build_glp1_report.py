from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
import sys

OUT = sys.argv[1]
PW, PH = 13.333 * inch, 7.5 * inch
TEAL = colors.HexColor("#0f6e74")
DEEP = colors.HexColor("#0b3f44")
MINT = colors.HexColor("#7fd1c7")
INK = colors.HexColor("#1b2a35")
GREY = colors.HexColor("#5b6770")
CARD = colors.HexColor("#f1f6f6")
WHITE = colors.white
M = 0.7 * inch

c = canvas.Canvas(OUT, pagesize=(PW, PH))
c.setTitle("GLP-1 Testing: Our Next Big Market")
c.setAuthor("myLAB Box internal")


def para(text, x, y_top, w, size=12, color=INK, bold=False, leading=None, align=0):
    st = ParagraphStyle("p", fontName="Helvetica-Bold" if bold else "Helvetica", fontSize=size,
                        leading=leading or size * 1.32, textColor=color, alignment=align)
    p = Paragraph(text, st)
    _, h = p.wrap(w, 1000)
    p.drawOn(c, x, y_top - h)
    return h


def header(kicker, title, n, dark=False):
    bg = DEEP if dark else WHITE
    c.setFillColor(bg)
    c.rect(0, 0, PW, PH, fill=1, stroke=0)
    c.setFillColor(MINT if dark else TEAL)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(M, PH - 0.75 * inch, kicker.upper())
    para(title, M, PH - 0.9 * inch, PW - 2 * M, size=27, color=WHITE if dark else INK, bold=True, leading=32)
    c.setFillColor(MINT if dark else GREY)
    c.setFont("Helvetica", 8)
    c.drawString(M, 0.38 * inch, "myLAB Box  ·  GLP-1 Testing  ·  October 2026  ·  Internal")
    c.drawRightString(PW - M, 0.38 * inch, f"{n} / 4")


def card(x, y, w, h, fill=CARD):
    c.setFillColor(fill)
    c.roundRect(x, y, w, h, 8, fill=1, stroke=0)


def stat(x, y_top, w, big, label, dark=True):
    c.setFillColor(MINT if dark else TEAL)
    c.setFont("Helvetica-Bold", 44)
    c.drawString(x, y_top - 44, big)
    para(label, x, y_top - 56, w, size=12, color=WHITE if dark else INK, leading=15.5)


# ---------- Slide 1: the opportunity ----------
header("The opportunity", "GLP-1 patients need lab tests on a schedule.<br/>We helped pioneer testing at home.", 1, dark=True)
top = PH - 2.55 * inch
colw = (PW - 2 * M) / 3
stat(M, top, colw - 30, "1 in 8", "U.S. adults say they are taking a GLP-1 drug right now (KFF, Nov 2025)")
stat(M + colw, top, colw - 30, "4–6", "blood panels per patient over two years: before the first dose, at month 3, then every 6–12 months")
stat(M + 2 * colw, top, colw - 30, "20%+", "growth in Quest’s consumer testing in 2025, to about $250M. The big labs see the demand.")
card(M, 0.75 * inch, PW - 2 * M, 1.75 * inch, fill=TEAL)
para("<b>Why this fits myLAB Box</b>", M + 22, 2.3 * inch, PW - 2 * M - 44, size=14, color=WHITE)
para("Every GLP-1 patient is a <b>repeat customer</b>, whichever drug or pharmacy they use. Most get care online and need labs that come to them. "
     "We have done exactly that since 2013, as one of the first companies to offer at-home lab screening. "
     "This is the market where our head start is worth the most.",
     M + 22, 1.98 * inch, PW - 2 * M - 44, size=13, color=WHITE, leading=18)
c.showPage()

# ---------- Slide 2: the market is moving ----------
header("Why now", "The race started in 2026. Seats are being taken.", 2)
items = [
    ("Labcorp & Quest", "GLP-1 baseline and follow-up panels for doctors and consumers. Quest’s consumer site grew ~35% in 2025."),
    ("Noom", "17-marker kit at $125, sold to its GLP-1 members. Uses an outside lab partner (Ash) for at-home testing."),
    ("SiPhox Health", "40+ marker GLP panel at $199, painless upper-arm collection, subscription model."),
    ("Everlywell", "$134 GLP-1 panel. Works with 4 of the 5 largest U.S. health plans (170M insured lives)."),
]
cw = (PW - 2 * M - 3 * 18) / 4
y0 = PH - 2.1 * inch
for i, (name, txt) in enumerate(items):
    x = M + i * (cw + 18)
    card(x, y0 - 2.35 * inch, cw, 2.35 * inch)
    c.setFillColor(TEAL)
    c.rect(x, y0 - 6, cw, 6, fill=1, stroke=0)
    para(f"<b>{name}</b>", x + 16, y0 - 22, cw - 32, size=15, color=INK)
    para(txt, x + 16, y0 - 52, cw - 32, size=11.5, color=INK, leading=15.5)
# money row
y1 = y0 - 2.75 * inch
para("<b>Investors are paying for testing tied to care</b>", M, y1, PW - 2 * M, size=14, color=TEAL)
money = [("$100M", "Nourish Series C (May 2026): metabolic clinic adding labs and GLP-1 care"),
         ("$7M", "Altro Health seed (Oct 2026): lets gyms and medspas offer GLP-1s and lab tests"),
         ("~$370M", "Ro’s estimated GLP-1 revenue in 2024. Platforms this size need a lab partner")]
mw = (PW - 2 * M) / 3
for i, (big, lab) in enumerate(money):
    x = M + i * mw
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 30)
    c.drawString(x, y1 - 58, big)
    para(lab, x, y1 - 68, mw - 30, size=11.5, color=INK, leading=15)
c.setFillColor(GREY)
para("Competitors are signing the telehealth and clinic partners now. Whoever is ready first gets the volume.",
     M, 1.0 * inch, PW - 2 * M, size=12.5, color=INK, bold=True)
c.showPage()

# ---------- Slide 3: how we win ----------
header("How we win market share", "Turn our pioneer head start into the GLP-1 testing leader.", 3)
lx, lw = M, 4.0 * inch
y = PH - 2.05 * inch
card(lx, 0.75 * inch, lw, y - 0.75 * inch)
para("<b>What we already have</b>", lx + 18, y - 18, lw - 36, size=14, color=TEAL)
have = ["A trusted at-home testing brand since 2013",
        "CLIA/CAP-certified partner labs",
        "A GLP-1 test on the market today ($159)",
        "Years of at-home test results newer players lack",
        "Testing-to-treatment and retail partner experience"]
yy = y - 50
for h in have:
    yy -= para("\u2022  " + h, lx + 18, yy, lw - 36, size=12, color=INK, leading=16) + 9
para("<b>What we lack</b>", lx + 18, yy - 14, lw - 36, size=14, color=TEAL)
para("A deeper panel, repeat business, partners and reliable delivery. All fixable with focus and funding.",
     lx + 18, yy - 40, lw - 36, size=12, color=INK, leading=16)
rx = lx + lw + 0.35 * inch
rw = PW - M - rx
para("<b>Five moves to win</b>", rx, y - 4, rw, size=14, color=TEAL)
moves = [("Fix delivery first", "Tracked kits both ways, results within 7 days, faster support. Patients on a 3-month schedule only reorder if it works."),
         ("Build the best GLP-1 panel", "Add HbA1c, B12, vitamin D, ferritin, lipase, hs-CRP. Baseline and Follow-up kits, priced near Noom and Everlywell."),
         ("Sell a schedule, not a kit", "Subscription that ships the next test at months 3, 6 and 12. HSA/FSA eligible."),
         ("Add a clinician step", "Abnormal results get a clinician review. That makes us part of care, which partners and insurers pay for."),
         ("Go where patients are", "White-label kits and an ordering link for GLP-1 telehealth, clinics, gyms and medspas.")]
yy = y - 36
for i, (t, d) in enumerate(moves, 1):
    c.setFillColor(TEAL)
    c.circle(rx + 14, yy - 12, 14, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(rx + 14, yy - 16.5, str(i))
    h = para(f"<b>{t}.</b> {d}", rx + 40, yy - 2, rw - 40, size=12, color=INK, leading=15.5)
    yy -= max(h, 30) + 12
c.showPage()

# ---------- Slide 4: the ask ----------
header("The ask", "Fund GLP-1 testing as its own program.", 4, dark=True)
y = PH - 2.0 * inch
para("Name one owner. Give it its own budget line. Hold it to 12-month targets.",
     M, y, PW - 2 * M, size=15, color=WHITE, leading=20)
# value row
y2 = y - 0.75 * inch
para("<b>What it could be worth (first-year sales at $159 × 4 tests)</b>", M, y2, PW - 2 * M, size=13, color=MINT)
vals = [("$1.6M", "2,500 customers", "0.025% of U.S. patients"),
        ("$6.4M", "10,000 customers", "0.1% of U.S. patients"),
        ("$15.9M", "25,000 customers", "0.25%, with partner deals")]
vw = (PW - 2 * M - 2 * 18) / 3
for i, (big, a, b) in enumerate(vals):
    x = M + i * (vw + 18)
    card(x, y2 - 1.75 * inch, vw, 1.4 * inch, fill=TEAL)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 34)
    c.drawString(x + 18, y2 - 0.9 * inch, big)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(x + 18, y2 - 1.2 * inch, a)
    c.setFillColor(MINT)
    c.setFont("Helvetica", 11)
    c.drawString(x + 18, y2 - 1.45 * inch, b)
# timeline
y3 = y2 - 2.05 * inch
para("<b>12-month plan</b>", M, y3, PW - 2 * M, size=13, color=MINT)
steps = [("Days 0–90", "Name the owner. Fix shipping and tracking. Finalize the new panel and price."),
         ("Months 3–6", "Launch Baseline and Follow-up kits and the subscription. Open partner talks."),
         ("Months 6–12", "Sign 2 partners. Reach 1,000+ subscribers. Publish our first GLP-1 results summary.")]
sw = (PW - 2 * M) / 3
c.setStrokeColor(MINT)
c.setLineWidth(2)
c.line(M + 7, y3 - 34, PW - M - sw + 7, y3 - 34)
for i, (t, d) in enumerate(steps):
    x = M + i * sw
    c.setFillColor(MINT)
    c.circle(x + 7, y3 - 34, 7, fill=1, stroke=0)
    para(f"<b>{t}</b>", x, y3 - 48, sw - 24, size=12.5, color=WHITE)
    para(d, x, y3 - 66, sw - 24, size=11, color=WHITE, leading=14.5)
para("Planning estimates, not forecasts. Customers who stay on treatment keep buying in year two (~2 tests a year). "
     "Sources: KFF (Nov 2025); J.P. Morgan Research (~10M U.S. patients, 2025); Quest Q4 2025 earnings; Labcorp (Mar 2024); Noom, SiPhox, Choose Health, "
     "Everlywell product pages and releases (2025–26); Fierce Healthcare (Nourish, May 2026); Fitt Insider (Altro, Oct 2026); Sacra (Ro, 2024); "
     "Business Wire (Ash–Noom, Dec 2025); mylabbox.com; CB Insights. All figures checked October 2026.",
     M, 0.95 * inch, PW - 2 * M, size=7.5, color=MINT, leading=9.5)
c.showPage()
c.save()
print("ok")
