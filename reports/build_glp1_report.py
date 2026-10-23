from reportlab.lib.pagesizes import letter
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, KeepTogether)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing, String, Rect
import sys

OUT = sys.argv[1]
INK = colors.HexColor("#1b2a35")
TEAL = colors.HexColor("#0f6e74")
LIGHT = colors.HexColor("#e7f2f2")
GREY = colors.HexColor("#5b6770")
AMBER = colors.HexColor("#b26b00")
RED = colors.HexColor("#a3312b")
GREEN = colors.HexColor("#2f7d3a")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=18,
                    textColor=TEAL, spaceBefore=6, spaceAfter=8)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=12.5,
                    textColor=INK, spaceBefore=10, spaceAfter=4)
B = ParagraphStyle("B", parent=ss["BodyText"], fontName="Helvetica", fontSize=9.6, leading=13.2,
                   textColor=INK, spaceAfter=6)
BUL = ParagraphStyle("BUL", parent=B, leftIndent=14, bulletIndent=4, spaceAfter=3)
SMALL = ParagraphStyle("S", parent=B, fontSize=8, leading=10.5, textColor=GREY)
CELL = ParagraphStyle("C", parent=B, fontSize=8.6, leading=11, spaceAfter=0)
CELLB = ParagraphStyle("CB", parent=CELL, fontName="Helvetica-Bold")
CALL = ParagraphStyle("CALL", parent=B, fontSize=10.5, leading=15, textColor=INK)


def p(t, s=B):
    return Paragraph(t, s)


def bullets(items):
    return [Paragraph(i, BUL, bulletText="•") for i in items]


def table(rows, widths, header=True, zebra=True):
    data = [[Paragraph(str(c), CELLB if (header and r == 0) else CELL) for c in row]
            for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c9d3d6")),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), TEAL), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white)]
        data[0] = [Paragraph(f'<font color="white">{c}</font>', CELLB) for c in rows[0]]
        t = Table(data, colWidths=widths, repeatRows=1)
    if zebra:
        for r in range(1, len(rows)):
            if r % 2 == 0:
                st.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#f4f8f8")))
    t.setStyle(TableStyle(st))
    return t


def callout(text):
    t = Table([[Paragraph(text, CALL)]], colWidths=[6.9 * inch])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                           ("LINEBEFORE", (0, 0), (0, -1), 3, TEAL),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                           ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    return t


def price_chart():
    items = [("Noom kit (members only)", 125, "17 markers"),
             ("Everlywell lab-visit panel", 134, "A1c, CMP, lipids"),
             ("myLAB Box At-Home GLP-1", 159, "thyroid, lipids, kidney, liver"),
             ("SiPhox GLP panel (launch)", 199, "40+ markers")]
    w, h = 6.9 * inch, 1.55 * inch
    d = Drawing(w, h)
    left, maxv, barh, gap = 165, 220.0, 16, 8
    top = h - 18
    d.add(String(0, h - 8, "Published price per GLP-1 panel (USD)", fontName="Helvetica-Bold",
                 fontSize=9, fillColor=INK))
    for i, (name, v, note) in enumerate(items):
        y = top - (i + 1) * (barh + gap) + gap
        bw = (w - left - 120) * v / maxv
        col = TEAL if "myLAB" in name else colors.HexColor("#9fb7bb")
        d.add(String(0, y + 6, name, fontName="Helvetica", fontSize=8.5, fillColor=INK))
        d.add(Rect(left, y, bw, barh, fillColor=col, strokeColor=None))
        d.add(String(left + bw + 5, y + 6, f"${v}  · {note}", fontName="Helvetica",
                     fontSize=8, fillColor=GREY))
    return d


def on_page(c, doc):
    c.saveState()
    c.setFont("Helvetica", 7.5)
    c.setFillColor(GREY)
    c.drawString(0.8 * inch, 0.5 * inch, "GLP-1 Testing Opportunity  ·  Briefing for the principals of myLAB Box  ·  October 2026")
    c.drawRightString(7.7 * inch, 0.5 * inch, f"Page {doc.page}")
    c.restoreState()


def cover(c, doc):
    c.saveState()
    c.setFillColor(TEAL)
    c.rect(0, 7.2 * inch, 8.5 * inch, 3.8 * inch, fill=1, stroke=0)
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 11)
    c.drawString(0.8 * inch, 10.2 * inch, "BRIEFING FOR THE PRINCIPALS OF myLAB BOX")
    c.setFont("Helvetica-Bold", 30)
    c.drawString(0.8 * inch, 9.3 * inch, "The GLP-1 Testing")
    c.drawString(0.8 * inch, 8.8 * inch, "Opportunity")
    c.setFont("Helvetica", 13)
    c.drawString(0.8 * inch, 8.2 * inch, "Why our GLP-1 testing program deserves more funding,")
    c.drawString(0.8 * inch, 7.95 * inch, "and what that money should build in the next 12 months")
    c.setFillColor(INK)
    c.setFont("Helvetica", 10)
    c.drawString(0.8 * inch, 6.6 * inch, "October 2026  ·  Internal  ·  Every figure fact-checked against public sources (see Appendix A)")
    c.restoreState()


story = []
story.append(Spacer(1, 4.6 * inch))
story.append(p("<b>The short version</b>", H2))
story += bullets([
    "Roughly <b>1 in 8 U.S. adults</b> report taking a GLP-1 drug right now (KFF, Nov 2025). Lab testing is part of safe treatment: a baseline panel, an early follow-up, then checks every 6 to 12 months.",
    "That makes GLP-1 monitoring a <b>repeat purchase</b>, not a one-time kit. Repeat purchases are the best kind of revenue a testing company can have.",
    "Competitors moved fast in 2026: Noom, SiPhox, Choose Health and Everlywell all launched GLP-1 panels. Investors put <b>$100M into Nourish</b> and <b>$7M into Altro Health</b>, both with lab testing in the model.",
    "myLAB Box already sells an At-Home GLP-1 Test ($159). We have the product, the CLIA/CAP lab network and a brand dating to 2013. We do not yet have the panel depth, the subscription model, the partner channel or the fulfillment record to win this category.",
    "<b>The ask:</b> fund GLP-1 testing as a dedicated program with its own budget, owner and 12-month targets (Section 7).",
])
story.append(PageBreak())

# 1
story.append(p("1. Why this matters now", H1))
story.append(p("The GLP-1 boom created a new, large group of patients who need blood work on a schedule. "
               "Drug prices and brand wars will keep shifting. The need for monitoring does not depend on which drug wins: "
               "every new patient on Wegovy, Zepbound, Ozempic, Mounjaro or a compounded version is a candidate for testing."))
story.append(table([
    ["Signal", "What the source says", "Source"],
    ["Current U.S. use", "12% of adults say they are taking a GLP-1 drug now; 18% have taken one at some point.", "KFF poll, Nov 2025"],
    ["Weight-loss use", "Adults using GLP-1 injections for weight loss rose from 5.8% (Feb 2024) to 12.4% (2025).", "Gallup, 2025 (n = 16,946)"],
    ["Prescription-based count", "About 10M Americans on treatment in 2025, projected at 25–30M by 2030.", "J.P. Morgan Research"],
    ["Utilization trend", "Use expected to keep rising through 2027, then level off 2028–2030 in commercial plans.", "Milliman"],
], [1.35 * inch, 4.0 * inch, 1.55 * inch]))
story.append(Spacer(1, 6))
story.append(p("<i>Note on the numbers:</i> self-reported surveys (KFF, Gallup) run higher than prescription-based counts (J.P. Morgan). "
               "Even the low figure of ~10M patients is a very large pool for a testing business.", SMALL))

story.append(p("Testing is built into the care pattern", H2))
story.append(p("There is no single national guideline yet, but clinical labs and prescribers converge on the same rhythm:"))
story += bullets([
    "<b>Baseline before the first dose:</b> HbA1c, metabolic panel or CMP (kidney and liver), lipids, TSH. Lipase and CBC in some cases.",
    "<b>Early check:</b> about 3 months after starting or changing dose.",
    "<b>Maintenance:</b> every 6 to 12 months once stable, sooner with kidney or liver concerns.",
    "<b>Nutrients:</b> B12, vitamin D, iron/ferritin, folate, flagged for rapid weight loss and reduced food intake.",
])
story.append(p("Each step is a test order. A patient who stays on therapy for two years can generate four to six panels."))

story.append(p("The big labs are already treating this as a product line", H2))
story += bullets([
    "<b>Labcorp</b> launched a Weight Loss Management portfolio in March 2024 (Baseline Test with 20+ markers; Tracking Test), and sells a GLP-1 baseline bundle on Labcorp OnDemand.",
    "<b>Quest</b> sells Weight Loss Journey panels (baseline, expanded, premium) on questhealth.com. Its consumer-initiated testing business brought in close to <b>$250M in 2025</b>, growing more than 20%; questhealth.com alone grew ~35% to a $100M run rate.",
])
story.append(callout("<b>What this means for us:</b> the two largest labs in the country built GLP-1 products and are growing direct-to-consumer sales "
                     "at 20%+. The demand is proven. The question for myLAB Box is whether we compete for it on purpose or by accident."))
story.append(PageBreak())

# 2
story.append(p("2. How big is the market?", H1))
story.append(p("Market research firms publish GLP-1 monitoring forecasts, but the figures vary widely and the categories overlap. "
               "We show them for direction only and rate our confidence in each. None of these should be quoted to outside parties as hard facts."))
story.append(table([
    ["Segment", "2025", "2034", "Growth/yr", "Confidence"],
    ["GLP-1 companion metabolic monitoring devices (Market Intelo)", "$9.8B", "$51.3B", "20.2%", "Low: single vendor report"],
    ["Obesity drug companion diagnostics (Market Intelo, report A)", "$2.1B", "$12.6B", "19.6%", "Low: conflicts with report B"],
    ["Obesity drug companion diagnostics (Market Intelo, report B)", "$2.3B", "$11.8B", "18.5%", "Low: conflicts with report A"],
], [2.9 * inch, 0.7 * inch, 0.7 * inch, 0.8 * inch, 1.8 * inch]))
story.append(Spacer(1, 6))
story.append(p("<b>The safer way to size it is bottom-up.</b> If ~10M U.S. patients each buy two to four panels a year, "
               "and the average panel sells for $125–$200 direct-to-consumer, U.S. GLP-1 monitoring is a "
               "<b>$2.5B to $8B a year</b> spend pool before payers and employers are counted. That is our own estimate from the inputs above, not a published figure."))

story.append(p("3. Who is competing", H1))
story.append(price_chart())
story.append(Spacer(1, 4))
story.append(table([
    ["Company", "GLP-1 offer", "Price", "What they have that we lack"],
    ["Noom", "Biomarker Test Kit, 17 markers incl. HbA1c, ApoB, Lp(a), B12, vitamin D (May 2026). Tasso+ finger device.", "$125", "Bundled with its GLP-1 prescribing and coaching; huge member base"],
    ["SiPhox Health", "GLP Monitoring Panel, 40+ markers, upper-arm collection, “GLP Tolerance Score”, body composition.", "$199 at launch; listed as a $75 add-on to membership", "Subscription model, 50,000+ users (company claim), HSA/FSA"],
    ["Everlywell", "Metabolic & GLP-1 Monitoring Panel via lab visit: A1c, glucose, insulin, CMP, lipids.", "$134", "Enterprise deals with 4 of the top 5 U.S. health plans (170M insured lives)"],
    ["Choose Health", "GLP-1 Health Monitoring Panels (Apr 2026). Basic: 8 markers incl. ALT/AST/GGT, eGFR, lipase.", "n/a", "Outcomes report built on 150,000+ at-home tests"],
    ["Function Health", "Membership with 100+ biomarkers, twice-yearly testing; Withings device integration.", "$365/yr (some sources: $499)", "Device data plus labs in one view"],
    ["Quest / Labcorp", "Baseline and tracking panels, consumer and physician-ordered.", "Varies", "Insurance billing, thousands of draw sites"],
    ["<b>myLAB Box</b>", "<b>At-Home GLP-1 Test: thyroid, lipids, kidney, liver.</b> Results 5–8 business days. Not available in NY.", "<b>$159</b>", "—"],
], [1.05 * inch, 2.75 * inch, 1.05 * inch, 2.05 * inch]))

# 4
story.append(p("4. Where the money is going", H1))
story.append(p("Investors and partners are paying for companies that combine GLP-1 care with lab testing:"))
story += bullets([
    "<b>Nourish</b> raised a <b>$100M Series C</b> (May 2026, led by Menlo Ventures) to grow from dietitian care into a metabolic clinic that adds lab testing and GLP-1 prescribing.",
    "<b>Altro Health</b> raised a <b>$7M seed</b> (Oct 2026, led by NFX) for a platform letting gyms, trainers and medspas offer GLP-1s and lab testing. 500+ businesses on it.",
    "<b>Ash Wellness</b> runs at-home testing for <b>Noom</b>’s Microdose GLP-1Rx program (Dec 2025) and is listed as a LifeMD at-home lab partner.",
    "<b>Ro</b> generated an estimated <b>~$370M in GLP-1 revenue in 2024</b> (Sacra estimate) on ~$145/month memberships. Platforms of that size need a lab partner.",
    "<b>Everlywell</b> appointed a new Chief Commercial Officer and Chief Product Officer (Sept 2026) to grow its enterprise business around cardiometabolic health.",
])
story.append(callout("<b>The pattern:</b> the money is going to companies that sit inside a care program (telehealth, clinics, payers), "
                     "not to stand-alone kits. A test that changes a prescribing or dosing decision gets paid for. A test that only reports numbers becomes a commodity."))

# 5
story.append(p("5. Where myLAB Box stands today", H1))
story.append(table([
    ["We have", "We need"],
    ["A live At-Home GLP-1 Test at $159", "A deeper panel: HbA1c, B12, vitamin D, ferritin, lipase, hs-CRP. Noom ships most of these at $125."],
    ["CLIA/CAP-certified partner labs; FDA-registered company", "A subscription or repeat-test plan tied to the baseline, 3-month and 6–12-month schedule"],
    ["A brand in at-home testing since 2013 and a testing-to-treatment offer", "A clinician review step when a result is abnormal, so the test drives a care decision"],
    ["A retail/telehealth partner channel (eDrugstore.com partnership, Feb 2026)", "White-label kits for GLP-1 telehealth platforms; HSA/FSA eligibility"],
    ["Years of test results across many product lines", "A GLP-1 outcomes data set we can show to partners and payers (Choose Health is publishing one)"],
], [3.0 * inch, 3.9 * inch]))
story.append(Spacer(1, 8))
story.append(p("The risk we must fix first", H2))
story.append(p("Our public reviews hurt us in exactly the category where reliability matters most. myLAB Box holds a <b>TrustScore of about 2 out of 5</b> on Trustpilot. "
               "The repeated complaints are slow shipping, missing tracking, slow results and slow replies from support. A GLP-1 patient on a 3-month recheck schedule "
               "will not reorder from a company that lost their last kit, and no telehealth partner will sign a white-label deal after reading those reviews. "
               "Part of the new budget has to go to fulfillment and support, or the rest of the spending will not pay off."))
story.append(PageBreak())
# 6
story.append(p("6. What a funded program could earn (illustrative)", H1))
story.append(p("These scenarios use our current $159 price and the care schedule in Section 1. They are planning figures, not forecasts. "
               "Year one assumes 4 panels per patient (baseline, 3-month, 6-month, 12-month). Year two assumes 2 maintenance panels."))
story.append(table([
    ["Scenario", "Active GLP-1 patients", "Year-1 revenue (4 × $159)", "Year-2 revenue from same patients (2 × $159)", "Share of ~10M U.S. patients"],
    ["Conservative", "2,500", "$1.59M", "$0.80M", "0.025%"],
    ["Base", "10,000", "$6.36M", "$3.18M", "0.1%"],
    ["Stretch (with 1–2 partner deals)", "25,000", "$15.90M", "$7.95M", "0.25%"],
], [1.6 * inch, 1.1 * inch, 1.3 * inch, 1.6 * inch, 1.3 * inch]))
story.append(Spacer(1, 6))
story.append(p("Assumptions to test before we commit: retention between tests, any subscription discount, partner wholesale pricing (lower per kit, far lower acquisition cost), "
               "and lab and shipping cost per kit. For reference, a Hedgeye analyst note on Quest models year-one GLP-1 testing revenue per patient near $690–$980; "
               "we could not access the full note, so treat that range as unconfirmed.", SMALL))
story.append(callout("<b>The math is simple:</b> capturing one tenth of one percent of U.S. GLP-1 patients is a ~$6M first-year line, "
                     "and those patients keep buying the next year."))

# 7
story.append(p("7. The ask: fund GLP-1 testing as its own program", H1))
story.append(p("We ask the principals to approve a dedicated GLP-1 testing program with a named owner, its own budget line and the four workstreams below. "
               "Budget amounts to be set with finance once we have per-kit cost and partner pricing."))
story.append(table([
    ["Workstream", "What the money buys", "Done when"],
    ["1. Fix fulfillment and support", "Tracked outbound and return shipping, result-time SLA, support staffing, review recovery", "Median results under 7 days; TrustScore above 4"],
    ["2. Upgrade the panel", "Add HbA1c, B12, vitamin D, ferritin, lipase, hs-CRP; build Baseline and Follow-up versions", "New panels live at a price within $25 of Noom/Everlywell"],
    ["3. Subscription and care pathway", "Recheck plan on the 3-month / 6–12-month schedule; clinician review of abnormal results; HSA/FSA", "First 1,000 subscribers; reorder rate tracked monthly"],
    ["4. Partner channel", "White-label kit and ordering API for GLP-1 telehealth, clinics, gyms and medspas", "2 signed partners within 12 months"],
], [1.6 * inch, 3.3 * inch, 2.0 * inch]))
story.append(Spacer(1, 8))
story.append(p("Proposed timeline", H2))
story += bullets([
    "<b>Days 0–90:</b> name the owner, fix shipping and tracking, finalize the expanded panel, price the subscription.",
    "<b>Months 3–6:</b> launch Baseline and Follow-up panels and the recheck subscription; start partner sales conversations.",
    "<b>Months 6–12:</b> sign the first two partners; publish a first GLP-1 results summary from our own anonymized data.",
])
story.append(p("Risks to watch", H2))
story += bullets([
    "<b>Price pressure:</b> Noom is at $125 with 17 markers. We compete on depth, convenience and reliability, not on being cheapest.",
    "<b>Wellness vs. clinical:</b> without a clinician step, our test reads as a wellness product and loses partner and payer interest.",
    "<b>State limits:</b> our GLP-1 test is not sold in New York today; partner deals will need full state coverage.",
    "<b>Incumbents:</b> Quest and Labcorp bill insurance. Our edge is at-home convenience and white-label speed.",
])
story.append(Spacer(1, 14))

# Appendix A
story.append(p("Appendix A. Fact-check of the original research notes", H1))
story.append(p("The notes behind this proposal were checked claim by claim against public sources in October 2026. "
               "Confirmed figures were kept. Wrong or unsupported figures were corrected or removed from the report above."))
OK = '<font color="#2f7d3a"><b>Confirmed</b></font>'
FIX = '<font color="#a3312b"><b>Corrected</b></font>'
UNV = '<font color="#b26b00"><b>Unverified</b></font>'
story.append(table([
    ["Claim in the original notes", "Status", "What the sources show"],
    ["myLAB Box GLP-1 panel costs $149", FIX, "Product page lists the At-Home GLP-1 Test at <b>$159</b>."],
    ["myLAB Box founded in 2013", OK, "2013 per CB Insights and a company press release; some reviews say 2014."],
    ["myLAB Box reviews cite shipping delays and support complaints", OK, "Trustpilot TrustScore ~2/5; shipping, tracking and response time are the main complaints."],
    ["Over 38 million Americans on a GLP-1", FIX, "Surveys: ~12% of adults (KFF), roughly 30M people. Prescription-based: ~10M (J.P. Morgan). 38M not found."],
    ["Monitoring device penetration only ~22%", UNV, "No source found. Removed."],
    ["50M+ global patients in 2026; 200M+ by early 2030s", UNV, "No credible global count found. Removed."],
    ["Companion diagnostics market $4.1B → $22.8B, 19.5%", FIX, "Not found. Closest reports: $2.1B → $12.6B (19.6%) and $2.3B → $11.8B (18.5%), same publisher, conflicting."],
    ["Metabolic monitoring devices $9.8B → $51.3B, 20.2%", OK, "Matches a Market Intelo report. Single source, low confidence."],
    ["Devices for GLP-1 patients $0.8B → $5.2B, 22.8%", UNV, "Not found. Removed."],
    ["Hedgeye: $690–$980 year one, $400–$500 after, per patient at Quest", UNV, "Hedgeye note on Quest and GLP-1 testing exists but is paywalled; figures could not be checked."],
    ["Quest consumer testing > $250M in 2025, growth > 30% in 2026", FIX, "Close to $250M in 2025, growth > 20%. Outlook is 20–30%, not “over 30%”."],
    ["Labcorp weight-loss testing portfolio", OK, "Launched March 2024 (Baseline and Tracking tests)."],
    ["Labcorp 7,000+ draw locations for GLP-1 bloodwork", UNV, "Not confirmed. Removed."],
    ["CMS 2025: CGM coverage for all Medicare type 2 patients regardless of insulin", FIX, "Wrong. 2023 expansion covers insulin users and some patients with hypoglycemia. Broader non-insulin coverage was still pending in 2026."],
    ["SiPhox $199 panel, 40+ markers, GLP Tolerance Score, 50,000+ users", OK, "Matches YC launch page and company site. The site lists the panel as a $75 add-on to membership."],
    ["Noom $125 kit, 17 markers, Tasso+", OK, "Confirmed, May 2026, U.S. members only."],
    ["Choose Health panels, 150,000+ tests", OK, "Launched April 9, 2026; outcomes report based on 150,000+ tests announced."],
    ["Function: 160+ biomarkers, $365/yr, Withings integration", FIX, "Withings integration and $365 confirmed (some sources say $499). Biomarker count is 100+, not 160+."],
    ["Everlywell: 4 of top 5 health plans, 170M lives", OK, "Confirmed in Everlywell releases (2025, Sept 2026)."],
    ["Altro Health $7M seed; Nourish $100M Series C", OK, "Confirmed: Altro Oct 2026 (NFX); Nourish May 2026 (Menlo)."],
    ["Ro GLP-1 revenue ~$370M", OK, "Sacra estimate for 2024. Not a company-reported figure."],
    ["LifeMD partnered with Ash Wellness", OK, "Listed in secondary sources; Ash–Noom GLP-1 deal confirmed (Dec 2025)."],
    ["LivIQ – RedDrop; Nightingale – Supernormal partnerships", UNV, "No sources found. Removed."],
    ["Testing cadence: baseline, every 6–12 months, symptom-triggered", OK, "Matches clinical lab guidance; many add a 3-month early check."],
], [2.35 * inch, 0.8 * inch, 3.75 * inch]))
story.append(PageBreak())

# Appendix B
story.append(p("Appendix B. Sources", H1))
src = [
    "KFF poll, 1 in 8 adults currently taking a GLP-1 (Nov 2025): kff.org/health-costs/poll-1-in-8-adults-say-they-are-currently-taking-a-glp-1-drug-for-weight-loss-diabetes-or-another-condition-even-as-half-say-the-drugs-are-difficult-to-afford/",
    "Gallup obesity and GLP-1 index (2025), via Patient Care: patientcareonline.com/view/us-obesity-rates-decline-in-tandem-with-rise-in-use-of-glp-1-ra-new-gallup-index-shows",
    "J.P. Morgan Research, obesity drugs outlook: jpmorgan.com/insights/global-research/current-events/obesity-drugs",
    "Milliman, long-range GLP-1 forecast for health plans: milliman.com/en/insight/long-range-glp-1-forecast-health-plans",
    "Labcorp Weight Loss Management launch (Mar 2024): labcorp.com/labcorp-launches-weight-loss-management-testing-solutions",
    "Labcorp OnDemand GLP-1 testing: ondemand.labcorp.com/glp1-testing",
    "Quest Weight Loss Journey panels: questhealth.com/product/weight-loss-journey-test-panel-baseline/13233.html",
    "Quest consumer testing, 360Dx: 360dx.com/node/109561 ; Quest Q4 2025 webcast script: s2.q4cdn.com/390454341/files/doc_financials/2025/q4/Quest-Diagnostics-2025-Q4-Year-End-Webcast-Script.pdf",
    "Quest Q2 2026 earnings call highlights: marketbeat.com/instant-alerts/quest-diagnostics-q2-earnings-call-highlights-2026-07-23/",
    "Hedgeye, DGX GLP-1 adoption drives testing volume (paywalled): app.hedgeye.com/insights/182259",
    "Market Intelo, GLP-1 companion metabolic monitoring devices: marketintelo.com/report/glp-1-companion-metabolic-monitoring-devices-market",
    "Market Intelo, obesity drug companion diagnostics: marketintelo.com/report/obesity-drug-companion-diagnostics-market",
    "myLAB Box At-Home GLP-1 Test: mylabbox.com/product/at-home-glp-1-test/",
    "myLAB Box Trustpilot: trustpilot.com/review/mylabbox.com",
    "myLAB Box company profile: cbinsights.com/company/mylab ; Paste Magazine: pastemagazine.com/science/mylab-box/mylab-box-brings-std-testing-home",
    "Noom biomarker kit (May 2026): fiercehealthcare.com/health-tech/noom-launches-home-biomarker-test-kit-metabolic-health-monitoring",
    "SiPhox GLP monitoring launch: ycombinator.com/launches/Qel-siphox-health-glp-monitoring ; siphoxhealth.com/panels",
    "Choose Health GLP-1 panels (Apr 2026): smb.americanpress.com/article/Choose-Health-Launches-Comprehensive-At-Home-GLP-1-Monitoring-Panels-for-Ozempic-Wegovy-and-Mounjaro-Users/69d79ef90f25261839c247a0",
    "Everlywell Metabolic & GLP-1 panel: everlywell.com/everywhere/tests/metabolic-glp-1-monitoring-panel/",
    "Everlywell executive appointments (Sept 2026): businesswire.com/news/home/20260924145467/en/",
    "Function and Withings: withings.com/pages/withings-function ; Equinox/Function pricing: athletechnews.com/equinox-adds-biomarker-lab-tests-function-health/",
    "Nourish $100M Series C: fiercehealthcare.com/finance/nourish-raises-100m-plans-expand-care-model-physicians",
    "Altro Health $7M seed: insider.fitt.co/altro-health-raises-7m-to-build-clinical-wellness-infrastructure/",
    "Ash and Noom GLP-1 program (Dec 2025): businesswire.com/news/home/20251216686822/en/",
    "Ro GLP-1 revenue estimate: sacra.com/research/ro",
    "Medicare CGM coverage (2023 expansion): diatribe.org/diabetes-management/medicare-expands-cgm-coverage-people-type-2-diabetes ; medtechdive.com/news/dexcom-abbott-await-medicare-coverage-expansion-for-cgms/828775/",
    "GLP-1 lab monitoring guidance: clinicallabs.com.au/doctor/articles/monitoring-patients-on-glp1-agonists ; labfinder.com/2025/11/glp-1-weight-loss-medications-and-lab-tests-a-simple-guide-to-staying-safe-and-on-track/",
]
for i, s in enumerate(src, 1):
    story.append(Paragraph(f"{i}. {s}", SMALL))
story.append(Spacer(1, 10))
story.append(p("All figures from third-party sources were checked in October 2026. Company-reported numbers (user counts, outcomes data sets) are the companies’ own claims. "
               "Section 6 revenue scenarios are internal planning estimates.", SMALL))

doc = SimpleDocTemplate(OUT, pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                        topMargin=0.75 * inch, bottomMargin=0.8 * inch,
                        title="The GLP-1 Testing Opportunity", author="myLAB Box internal briefing")
doc.build(story, onFirstPage=cover, onLaterPages=on_page)
print("ok")
