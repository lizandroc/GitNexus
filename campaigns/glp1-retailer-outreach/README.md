# Monitored GLP-1 — Campaign & Dashboard

A Dripify-style outreach campaign and tracking dashboard for **myLAB Box GLP-1 at-home
testing (Enterprise & Wholesale)**, targeting B2B enterprise buyers and GLP-1 retailer /
reseller partners.

- **Landing page:** mylabboxweightloss.com — source in [`lizandroc/mylabbox-gpl-1`](https://github.com/lizandroc/mylabbox-gpl-1)
- **Dashboard:** open `dashboard.html` in any browser (self-contained, no build or server needed)

---

## What's here

```
campaigns/glp1-retailer-outreach/
├── dashboard.html              ← the dashboard (generated — do not edit by hand)
├── dashboard.template.html     ← dashboard source; edit this
├── build.mjs                   ← injects campaign.json into the template
├── sequences.md                ← the four drip sequences, full copy
├── data/
│   └── campaign.json           ← single source of truth for every number
└── strategy/
    ├── icp-and-segments.md     ← two partner motions, six segments, qualification
    ├── messaging.md            ← positioning, proof points, objection handling
    └── compliance.md           ← guardrails · READ §1b BEFORE LAUNCH
```

## Two partner motions

The campaign mirrors the landing page's own structure. Every prospect is routed to one:

| | **Motion A — Provider Partnership** | **Motion B — Enterprise & Wholesale** |
|---|---|---|
| Who | Weight loss clinics, med spas, telehealth prescribers | Telehealth platforms, employers, pharmacies, health systems |
| Mechanic | They recommend, the patient orders via the provider portal, they earn per kit | Volume pricing, direct-to-patient fulfilment to their population |
| Recurrence | Monitoring every 3–4 months → 3–4 orders per patient per year | Same cadence, bought at volume |
| Sequence | SEQ-A | SEQ-C |

## Segments

Mapped to the landing page's own organization-type picker, so inbound and outbound share
one taxonomy.

| ID | Segment | Page org type | Motion | Sequence |
|----|---------|---------------|--------|----------|
| S1 | Weight loss clinics & med spas | Medical weight loss clinic | A | SEQ-A |
| S2 | Telehealth platforms | Telehealth platform | A or B | SEQ-B |
| S3 | Pharmacies | Pharmacy | B | SEQ-B |
| S4 | Employers & benefits | Employer / benefits program | B | SEQ-C |
| S5 | Health systems | Health system | B | SEQ-C |
| S6 | Gyms, clubs & wellness | Other | B | SEQ-B |

## Sequences

| ID | Name | Segments | Length | Channel | Automation |
|----|------|----------|--------|---------|------------|
| SEQ-A | SMB Velocity | S1 | 18 days, 9 steps | LinkedIn-primary | eligible |
| SEQ-B | Mid-Market Multichannel | S2, S3, S6 | 30 days, 11 steps | Email-primary | email only |
| SEQ-C | Enterprise ABM | S4, S5 | 45 days, 12 steps | Fully manual | none |
| SEQ-D | Re-engagement | all | 60 days, 5 steps | Email only | email only |

Steps use Dripify-style primitives (`VIEW`, `CONNECT`, `LI-MSG`, `INMAIL`, `EMAIL`, `WAIT`,
`IF`, `TASK`), so they port to Dripify, HeyReach, Expandi, Smartlead, Instantly, Outreach
or Salesloft without rewriting.

---

## ⚠️ Two gates before this campaign sends

**1. Provider compensation review.** Motion A pays a provider per kit for a test they
recommend to their own patient. Medicare's GLP-1 Bridge (live July 1, 2026) puts federal
beneficiaries into that population, which pulls the structure toward the **Anti-Kickback
Statute, EKRA, Stark** and state analogues. This needs healthcare regulatory counsel in
writing. **If Motion A is restricted, the campaign still runs on Motion B** — the sequences
are written to be separable. See `strategy/compliance.md` §1b.

**2. LinkedIn automation decision.** LinkedIn's User Agreement prohibits automated access.
Cloud tools like Dripify operate against that regardless of configuration, and the account
at risk belongs to the rep. `strategy/compliance.md` §5 lays out the risk, mandatory limits
if you proceed, and three safer alternatives. **Recommended:** run email-primary with manual
LinkedIn touches; reserve automation for S1 only, if at all.

Also before launch: NY-only organizations suppressed at the list stage (the test is
temporarily unavailable in NY), and every `[PLACEHOLDER]` in `sequences.md` replaced or removed.

---

## The dashboard

Open `dashboard.html` directly — no server, no build, no network.

**Views:** KPI row with targets · pipeline funnel · reply rate by segment · weekly activity
(small multiples) · sequence board with per-step in-flight counts · attainment vs target ·
sortable prospect table with contact emails.

**Behaviour:** the segment chips scope every chart at once. Each chart has a table-view twin
for the values, and hover tooltips throughout. Light by default — dark is available through
the in-page toggle and is not driven by your OS or host theme.

### Swapping in real data

Everything in `data/campaign.json` is **sample data** — the figures are illustrative and the
account names, contacts and email addresses are fictional, so the views could be reviewed
before launch. To use it for real:

1. Edit `data/campaign.json` with real exports.
2. Set `"dataMode": "live"` and remove the sample banner from `dashboard.template.html`.
3. Run `node build.mjs`.

`weeklyBySegment[segment][metric][week]` holds the real per-segment weekly values. Its
margins must be exact in **both** directions: each segment's row sums to that segment's
total, and each week's column sums to the campaign total in `weekly`. That is what keeps a
filtered trend line agreeing with the KPI tile above it — the earlier version apportioned
campaign totals by segment share, which produced trends that quietly contradicted the tiles.

`build.mjs` refuses to write if anything doesn't reconcile — funnel stages, and every row
and column of every `weeklyBySegment` metric — so a bad export fails loudly instead of
rendering a plausible wrong dashboard. KPI deltas and all rate targets are derived from the
data rather than stored, so they can't drift out of date.

```bash
node build.mjs
# dashboard.html written — 6 segments, 4 sequences, 16 sample accounts
```

### Design notes

Charts follow the repo's dataviz conventions: no dual-axis anywhere (the three weekly
measures are small multiples, not two y-scales), a single hue for single-series bars, an
ordinal ramp for the ordered funnel stages, and the diverging blue/red pair only where the
encoding is genuinely above/below target — with a signed `pts` label so colour is never the
only channel. The categorical and ordinal palettes were checked with the dataviz
validator for both light and dark surfaces.

---

## Targets (Q3 2026)

| Metric | Target |
|---|---|
| Accounts sourced | 2,400 |
| Prospects contacted | 1,800 |
| Reply rate (blended) | 9.0% |
| Positive reply rate | 3.4% |
| Meetings booked | 96 |
| SQLs | 54 |
| Partner agreements signed | 12 |
| Pipeline created | $2.1M |

Reply rates below 4% after 200+ sends mean the targeting is wrong, not the copy. Fix the
list before rewriting the message.
