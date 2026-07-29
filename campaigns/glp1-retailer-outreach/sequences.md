# Drip Sequences — "Monitored GLP-1"

Four sequences, mapped to the tiers in `strategy/icp-and-segments.md`. Steps use
Dripify-style primitives so they port directly into Dripify, HeyReach, Expandi,
Smartlead, Instantly, Outreach or Salesloft.

**Step types:** `VIEW` (profile view) · `FOLLOW` · `CONNECT` (invite, ±note) ·
`LI-MSG` (LinkedIn message) · `INMAIL` · `EMAIL` · `WAIT` · `IF` (branch) · `TASK` (manual)

**Before you launch anything here:** read `strategy/compliance.md` §5 on LinkedIn
automation risk, and replace every `[PLACEHOLDER]`. Merge fields are `{{like_this}}`.

---

## Global rules

| Rule | Value |
|---|---|
| Business days only | Mon–Thu send, Fri for follow-ups only |
| Send window | 08:00–16:00 in the prospect's timezone |
| Max cadence | 1 message per channel per person per week |
| Exit triggers | Any reply · meeting booked · opt-out · manual suppression · account marked closed-lost |
| Reply handling SLA | 4 business hours |
| A/B split | Step 1 subject/opener only; hold everything else constant; ≥200 sends per arm before calling it |

---

## SEQ-A · SMB Velocity

**Segments:** S1 Medical weight loss clinics & med spas · **Motion A — Provider Partnership**
**Length:** 18 days, 9 steps · **Channel:** LinkedIn-primary, email backup
**Automation:** eligible (the only sequence that is — see compliance §5)
**Goal:** book a 15-minute call

> ⚠️ **Do not launch SEQ-A until counsel has cleared the provider compensation structure**
> (`strategy/compliance.md` §1b). If Motion A is restricted, route S1 to SEQ-B instead.
> No message in this sequence may quote or estimate what a partner earns.

| # | Day | Type | Detail |
|---|-----|------|--------|
| 1 | 0 | `VIEW` | Profile view — no message |
| 2 | 1 | `CONNECT` | Invite **with** note (A1) |
| 3 | — | `IF` | Accepted → step 4 · Not accepted by day 10 → step 7 (email track) |
| 4 | +2 after accept | `LI-MSG` | Message A2 |
| 5 | +4 | `LI-MSG` | Message A3 — the value nudge |
| 6 | +5 | `LI-MSG` | Message A4 — the breakup |
| 7 | 10 | `EMAIL` | Email A5 (non-accepters only) |
| 8 | 14 | `EMAIL` | Email A6 |
| 9 | 18 | `EMAIL` | Email A7 — close the loop |

### A1 · Connection note (≤300 characters)

```
Hi {{first_name}} — I work with weight-loss clinics adding at-home lab monitoring
to their GLP-1 programs, mostly the ones tired of sending patients out for a draw.
Would like to follow what you're building at {{company}}.
```

### A2 · First message (day +2 after accept)

```
Thanks for connecting, {{first_name}}.

Quick question rather than a pitch: when a patient says yes to your weight program,
what happens next on the lab side — do you send them out for a draw, or skip labs?

Asking because that step is where most of the med spas I talk to lose people
between "interested" and "first dose."
```

### A3 · Value nudge (day +4)

```
{{first_name}} — the reason I asked:

we run a 10-biomarker panel — thyroid, lipids, kidney and liver — as an at-home
kit. Patient collects it in about five minutes, no clinic visit, results back in
3–5 days from when the lab receives the sample. CLIA-certified, CAP-accredited labs.

For a clinic it works like this: you recommend it, your patient orders through our
provider portal, and you earn on every kit. No inventory, no fulfillment, no
minimums. And because monitoring runs every 3–4 months, it's not a one-time order.

Worth 15 minutes? Happy to just send details instead if that's easier.
```

### A4 · Breakup (day +5)

```
No worries if this isn't a fit, {{first_name}} — I'll leave it here.

If it's useful later: the short version is at mylabboxweightloss.com. Good luck
with the program either way.
```

### A5 · Email, non-accepters (day 10)

> **Subject:** the draw site
> **Alt subject (B):** question about {{company}}'s weight program

```
{{first_name}},

When someone signs up for your weight program, do they have to go somewhere for
labs before they start?

That trip is where a lot of med spas quietly lose the sale. We run the same panel
— thyroid, lipids, kidney, liver — as an at-home kit under your brand, CLIA lab on
the back end. It takes the step out.

Is that a problem worth 15 minutes, or are labs not part of your program today?

{{sender_name}}
{{sender_title}}, myLAB Box
{{physical_address}}
{{unsubscribe_link}}
```

### A6 · Email follow-up (day 14)

> **Subject:** re: the draw site

```
{{first_name}} — following up once.

The reason this is coming up now: Medicare's GLP-1 Bridge went live July 1, so the
patient population on these drugs is about to get bigger — and older. More of those
patients need a baseline and a monitoring cadence than the cash-pay population did.

Want me to send the panel details and pricing, or should I close the file?

{{sender_name}}
{{physical_address}} · {{unsubscribe_link}}
```

### A7 · Close the loop (day 18)

> **Subject:** closing the file

```
{{first_name}} — assuming this isn't a priority, so I'll stop here.

If labs ever become part of the program, we're at mylabboxweightloss.com. No
follow-up needed.

{{sender_name}}
{{physical_address}} · {{unsubscribe_link}}
```

---

## SEQ-B · Mid-Market Multichannel

**Segments:** S2 Telehealth platforms · S3 Pharmacies · S6 Gyms & clubs · **Motion A or B by volume**
**Length:** 30 days, 11 steps · **Channel:** email-primary, manual LinkedIn touches
**Automation:** email only; LinkedIn steps are `TASK` (manual)
**Goal:** book a 30-minute discovery

| # | Day | Type | Detail |
|---|-----|------|--------|
| 1 | 0 | `TASK` | Research: trigger event, program page, who owns clinical |
| 2 | 0 | `VIEW` | Manual profile view |
| 3 | 1 | `EMAIL` | Email B1 — trigger-anchored |
| 4 | 3 | `TASK` | `CONNECT` with note B2 (manual) |
| 5 | 5 | `EMAIL` | Email B3 — the segment-specific case |
| 6 | 8 | `TASK` | `LI-MSG` B4 (if connected) |
| 7 | 12 | `EMAIL` | Email B5 — proof / resource |
| 8 | 16 | `TASK` | Multithread: identify + sequence a second persona |
| 9 | 19 | `EMAIL` | Email B6 — to the second persona |
| 10 | 24 | `EMAIL` | Email B7 — the direct ask |
| 11 | 30 | `EMAIL` | Email B8 — breakup, offer the nurture |

### B1 · Trigger-anchored opener (day 1)

> **Subject:** {{company}} + {{trigger_short}}
> **Alt (B):** the step between consult and first dose

```
{{first_name}},

Saw {{trigger_event}} — congrats.

One question as you scale that: how are you handling baseline and follow-up labs?
Most of the {{segment_noun}} we work with are either sending people to a draw site
or skipping labs, and both get expensive at volume — the first in conversion, the
second in liability.

We supply that layer white-label: the panel your provider would order, collected
at home, results into your system, CLIA-certified lab behind it.

Is lab workflow something you own, or does that sit with {{clinical_owner_role}}?

{{sender_name}}
{{sender_title}}, myLAB Box
{{physical_address}} · {{unsubscribe_link}}
```

### B2 · Connection note (day 3, manual)

```
Hi {{first_name}} — emailed you about lab workflow for {{company}}'s weight
program. Connecting here in case it's an easier channel. Happy to be useful either
way.
```

### B3 · Segment case (day 5)

Use the block for the prospect's segment.

> **Subject:** re: {{company}} + {{trigger_short}}

**S2 Telehealth**
```
{{first_name}} — the version of this that matters for a telehealth program:

your biggest measurable drop is usually between completed consult and first
shipment, and the draw-site requirement is a big piece of it. Removing it is a
conversion fix disguised as a clinical one.

Practically: kits ship within 24 hours, patient collects at home in about five
minutes, results come back digitally in 3–5 days from lab receipt. CLIA-certified,
CAP-accredited, physician-reviewed. At volume, kits ship direct to your members and
you get an account manager on the rollout.

Do you measure consult-to-first-dose today? Curious what the number looks like.
```

**S3 Pharmacy**
```
{{first_name}} — the version of this that matters for a pharmacy:

with the 503B bulks proposal in April, the compounding line has a visible end
date. The clinical-services line that replaces it needs to be durable. Monitoring
is recurring by design — every 3–4 months per patient — and it deepens a patient
relationship you already have.

We supply the kits, the lab network and the results; no inventory or fulfillment on
your side, and no minimums to start.

Worth a look at the economics at your script volume?
```

**S6 Gym / club**
```
{{first_name}} — the version of this that matters for a club:

the operators moving into GLP-1 programming all hit the same wall — you want the
clinical credibility without becoming a clinic. Lab monitoring is the cleanest
piece to own, because it's logistics, not medicine: your provider partner decides
the protocol, we handle collection and results, it's your brand on the kit.

It also gives you a quarterly member touchpoint that isn't a renewal email.

Is the GLP-1 program running yet, or still in design?
```

### B4 · LinkedIn message (day 8, manual, if connected)

```
{{first_name}} — not going to re-send what I emailed.

One thing that might be more useful: [PLACEHOLDER — link to a genuinely useful
asset, e.g. a monitoring-protocol checklist or the panel spec sheet]. Take it
whether or not we ever talk.

If lab workflow isn't yours, who should I be talking to?
```

### B5 · Proof / resource (day 12)

> **Subject:** the panel spec, in case it's useful

```
{{first_name}},

Sending the detail rather than another nudge.

A 10-biomarker panel from one at-home blood sample: TSH (thyroid); total
cholesterol, LDL, HDL and triglycerides (lipids); BUN and creatinine (kidney); AST
and ALT (liver).

Kits ship within 24 hours. Collection takes about five minutes — no clinic visit.
Results are physician-reviewed and delivered digitally, 3–5 days from lab receipt.
CLIA-certified, CAP-accredited affiliates, HIPAA-compliant reporting. If a result
needs attention, the patient gets a free consult with a physician licensed in their
state. No minimums to start.

One thing to flag up front: the panel is available across the US but temporarily
unavailable in NY.

Send me your rough monthly kit volume and I'll come back with real pricing. If not,
I'll assume the timing's wrong.

{{sender_name}}
{{physical_address}} · {{unsubscribe_link}}
```

### B6 · Second persona (day 19)

> **Subject:** lab workflow for {{company}}'s weight program

```
{{first_name}},

I've been talking to {{first_persona_name}} about how {{company}} handles baseline
and follow-up labs for the weight program — reaching out to you because this
usually lands on {{second_persona_role}} as much as anyone.

Short version: we supply at-home lab collection white-label, so patients don't
need a draw site. Relevant mostly if conversion or month-3 retention is on your
list this quarter.

Is that a real problem at {{company}}, or solved already?

{{sender_name}}
{{physical_address}} · {{unsubscribe_link}}
```

### B7 · The direct ask (day 24)

> **Subject:** worth 30 minutes?

```
{{first_name}} — I'll be direct.

I think there's a case here, but I can't build it without your numbers. Thirty
minutes, and I'll come back with the economics at your actual volume — including
if it doesn't clear its own cost, which happens.

{{calendar_link}}, or tell me it's not a fit and I'll stop.

{{sender_name}}
{{physical_address}} · {{unsubscribe_link}}
```

### B8 · Breakup (day 30)

> **Subject:** closing this out

```
{{first_name}} — closing the file, no hard feelings.

If it's a timing thing, tell me roughly when the compounded transition hits your
P&L and I'll come back a month before that. Otherwise I'll leave you alone.

{{sender_name}}
{{physical_address}} · {{unsubscribe_link}}
```

---

## SEQ-C · Enterprise ABM

**Segments:** S4 Employers & benefits programs · S5 Health systems · **Motion B — Enterprise & Wholesale**
**Length:** 45 days, 12 steps · **Channel:** fully manual, sales-led
**Automation:** **none.** Every step is a `TASK`.
**Goal:** a discovery meeting with 2+ stakeholders
**Account team:** AE + SDR + clinical SME on standby

| # | Day | Type | Detail |
|---|-----|------|--------|
| 1 | 0 | `TASK` | Account plan: map 3–5 personas, find the trigger, check for an active RFP (see compliance §6) |
| 2 | 1 | `TASK` | Warm path check — investors, advisors, board, alumni, existing customers |
| 3 | 2 | `EMAIL` | C1 to the clinical persona |
| 4 | 3 | `TASK` | `VIEW` + `FOLLOW` all mapped personas |
| 5 | 6 | `EMAIL` | C2 to the economic persona |
| 6 | 9 | `TASK` | `CONNECT` with note C3 — clinical persona |
| 7 | 14 | `EMAIL` | C4 — the point of view piece |
| 8 | 18 | `TASK` | `LI-MSG` or `INMAIL` C5 |
| 9 | 24 | `TASK` | Executive-to-executive touch — our VP/CEO to theirs |
| 10 | 30 | `EMAIL` | C6 — offer the clinical SME, not the demo |
| 11 | 38 | `TASK` | Physical or event touch — conference, dimensional mail, roundtable invite |
| 12 | 45 | `EMAIL` | C7 — the honest close |

### C1 · Clinical persona (day 2)

> **Subject:** Bridge volume and your draw capacity

```
{{first_name}},

A question about capacity rather than a pitch.

Medicare's GLP-1 Bridge went live July 1. Whatever share of that lands on
{{company}}'s weight-management service line, it arrives as patients who each need
a baseline panel and a repeat every 3–4 months. That's a draw-volume problem before
it's a clinical one, and outpatient phlebotomy is usually already at capacity.

We supply that layer as an at-home collection — one 10-biomarker panel (thyroid,
lipids, kidney, liver), CLIA-certified and CAP-accredited labs, physician-reviewed
results back digitally. Your protocol, executed without adding draw slots.

Is Bridge volume something you're actively modeling, or is it further down the list
than I'm assuming?

{{sender_name}}
{{sender_title}}, myLAB Box
{{physical_address}} · {{unsubscribe_link}}
```

### C2 · Economic persona (day 6)

> **Subject:** the monitoring cost of Bridge volume

```
{{first_name}},

Direct question about {{company}}'s weight-management economics.

Bridge brings patients in at a $50 copay, which is good for volume and hard on
margin per patient. The monitoring those patients need — baseline plus every 3–4
months — is real cost if it runs through your own phlebotomy and outpatient slots,
and it competes with visits you'd rather be doing.

At-home collection moves that cost off your footprint entirely: kits ship direct to
the patient, results come back physician-reviewed and digital, priced by volume with
no minimums.

I'm not going to claim a number at you without your volumes. If you'll share them
under NDA, I'll model it honestly — including the case where it doesn't pencil.

Worth a conversation?

{{sender_name}}
{{physical_address}} · {{unsubscribe_link}}
```

**S4 variant — Employers & benefits programs:**
```
{{first_name}},

GLP-1 is likely the fastest-growing line in your plan spend, and the hardest to
defend to a CFO — because pharmacy claims tell you what was dispensed, not whether
it's working or whether it's appropriate. Bridge going live July 1 only widens that.

Lab data closes part of the gap: baseline and periodic panels give you a real
utilization and safety signal instead of a fill count. We ship kits direct to your
population — no inventory or fulfillment on your side — with an account manager on
the rollout and volume-tiered pricing.

Is GLP-1 utilization management on the roadmap for the {{plan_year}} plan year?
```

### C3 · Connection note (day 9)

```
{{first_name}} — wrote to you about absorbing Bridge monitoring volume without
adding draw capacity. Connecting in case that's a better channel. Either way, happy
to send the CLIA/CAP documentation with nothing attached to it.
```

### C4 · Point of view (day 14)

> **Subject:** the post-compounding differentiator

```
{{first_name}},

Not a follow-up — a point of view you're free to disagree with.

Every operator in this category built on the same advantage: cheaper supply. That
advantage has a visible end date now. What I think replaces it is boring and
operational — the programs that win the next two years will be the ones that can
prove a patient was worked up properly, monitored on schedule, and retained past
month three.

That's not a marketing problem. It's an infrastructure one, and most operators are
carrying it as manual work across sites.

We built the infrastructure. But I'd genuinely like to hear where you think this
lands, because you're closer to it than I am.

Twenty minutes, no deck?

{{sender_name}}
{{physical_address}} · {{unsubscribe_link}}
```

### C5 · LinkedIn / InMail (day 18)

```
{{first_name}} — one line, then I'll stop crowding your inbox.

If lab monitoring across your sites is genuinely handled, tell me and I'll close
the file — no pitch, I'd just rather know. If it's half-handled, that's the
conversation I want.
```

### C6 · Offer the SME (day 30)

> **Subject:** our clinical lead, not a demo

```
{{first_name}},

Changing the offer. Instead of a demo, {{sme_name}}, who runs clinical for us,
will spend 30 minutes on how multi-site operators are actually structuring GLP-1
monitoring right now — what cadence, what panels, where it breaks.

No slides, no obligation, and useful whether or not you ever buy anything from us.
Worth it?

{{sender_name}}
{{physical_address}} · {{unsubscribe_link}}
```

### C7 · Honest close (day 45)

> **Subject:** last one

```
{{first_name}} — I've written a few times and haven't earned a reply, so this is
the last.

If I misread the priority, that's on me. If it's timing, tell me the quarter and
I'll come back then. If it's genuinely not relevant, that's a completely fine
answer and I'd rather have it than keep guessing.

Either way — good luck with what you're building.

{{sender_name}}
{{physical_address}} · {{unsubscribe_link}}
```

---

## SEQ-D · Re-engagement

**Audience:** no-reply exits from A/B/C after 90 days · closed-lost (timing/budget) · dormant partners
**Length:** 60 days, 5 steps · **Channel:** email only
**Goal:** re-open on a new trigger — never re-run the original pitch

| # | Day | Type | Detail |
|---|-----|------|--------|
| 1 | 0 | `TASK` | Verify still in role + still relevant; re-check suppression |
| 2 | 1 | `EMAIL` | D1 — new information, not a follow-up |
| 3 | 14 | `EMAIL` | D2 — a peer signal |
| 4 | 35 | `EMAIL` | D3 — the changed offer |
| 5 | 60 | `EMAIL` | D4 — permission to stop |

### D1 · New information (day 1)

> **Subject:** Bridge went live — does that change anything for you?

```
{{first_name}},

We spoke {{time_ago}} about lab monitoring and the timing wasn't right.

Two things changed since. Medicare's GLP-1 Bridge went live July 1 — eligible Part D
members at a $50 monthly copay, running through the end of 2027 — so the patient
population is widening. And in April the FDA proposed removing the GLP-1s from the
503B bulks list entirely, which closes the compounded-supply path.

More patients, less drug margin. If that's changing how you think about program
structure, I'm happy to be a sounding board — not pitching.

{{sender_name}}
{{physical_address}} · {{unsubscribe_link}}
```

### D2 · Peer signal (day 14)

> **Subject:** what {{segment_noun}} are doing about it

```
{{first_name}} — the pattern I'm seeing across {{segment_noun}} this quarter:
they're moving spend from acquisition to retention, because the drug itself no
longer differentiates. Monitoring keeps coming up because it's the one clinical
addition that's also a scheduled re-engagement event.

Is that the direction at {{company}}, or are you playing it differently?

{{sender_name}}
{{physical_address}} · {{unsubscribe_link}}
```

### D3 · Changed offer (day 35)

> **Subject:** smaller than last time

```
{{first_name}},

Last time we talked about a full program integration, which was probably too big a
first step.

The smaller version: a single-site or single-cohort start. There are no minimums and
no commitment, so it can genuinely be as small as you want it to be — you recommend
or order, we handle kits, shipping, lab processing and results.

If a smaller first step changes the answer, I'd like to know.

{{sender_name}}
{{physical_address}} · {{unsubscribe_link}}
```

### D4 · Permission to stop (day 60)

> **Subject:** should I stop?

```
{{first_name}} — one question, one word answer.

Should I check back in six months, or take you off the list entirely? Either is a
good answer and I'll honor it.

{{sender_name}}
{{physical_address}} · {{unsubscribe_link}}
```

---

## Benchmarks

Targets, not results. Track actuals against these in the dashboard.

| Sequence | Connect accept | Open | Reply | Positive reply | Meeting |
|---|---|---|---|---|---|
| SEQ-A · SMB | 32% | 46% | 11% | 4.2% | 2.4% |
| SEQ-B · Mid-market | 28% | 43% | 9% | 3.5% | 2.0% |
| SEQ-C · Enterprise | 24% | 51% | 7% | 3.0% | 1.8% |
| SEQ-D · Re-engagement | — | 38% | 6% | 2.2% | 1.1% |

Reply rates below 4% after 200+ sends mean the *targeting* is wrong, not the copy.
Fix the list before rewriting the message.
