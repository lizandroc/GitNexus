# Compliance Guardrails — GLP-1 B2B Outreach

Health-adjacent outreach carries real regulatory exposure. These are hard rules for
everything in this campaign: sequence copy, landing pages, sales calls, and the dashboard.

**Nothing here is legal advice.** Route the final sequence copy and the landing page
through counsel before launch. The rules below are the floor, not the ceiling.

---

## 1. The single most important rule

> **We sell diagnostics. We do not supply, source, prescribe, broker, or facilitate access
> to GLP-1 medication — and no asset in this campaign may imply that we do.**

Banned phrasings, no exceptions:

| ❌ Never write | ✅ Write instead |
|---|---|
| "Add GLP-1s to your offering" | "Add lab monitoring to your GLP-1 program" |
| "We help you sell semaglutide" | "We handle the baseline and monitoring labs" |
| "Get your patients on tirzepatide faster" | "Remove the draw-site trip between consult and first dose" |
| "Our GLP-1 program" | "Our GLP-1 monitoring panel" |
| "Guaranteed weight loss / results" | *(no outcome claims at all)* |
| "FDA-approved kit" | "CLIA-certified, CAP-accredited laboratory network" |

Do not use branded drug names (Ozempic, Wegovy, Zepbound, Mounjaro, Saxenda) in outbound
copy. They are trademarks of Novo Nordisk and Eli Lilly, they imply an affiliation we do
not have, and they attract filters. Say "GLP-1" or "GLP-1 program."

---

## 1b. ⚠️ Provider compensation — get this reviewed before the campaign sends

**This is the highest-risk item in the campaign and it is not a drafting problem.**

The Provider Partnership Program pays a provider **on every kit and every reorder** for a
test they recommend to their own patient. Structures that compensate a referral source per
test implicate:

- the **federal Anti-Kickback Statute (AKS)**, wherever a patient is a beneficiary of a
  federal healthcare program;
- the **Eliminating Kickbacks in Recovery Act (EKRA)**, which reaches laboratory referrals
  regardless of payer;
- the **Stark Law**, for physician referrals of designated health services including
  clinical laboratory services;
- state fee-splitting, self-referral and anti-kickback statutes, several of which are
  stricter than federal law.

**Medicare's GLP-1 Bridge makes this acute, not theoretical.** Before July 1, 2026 a
cash-pay GLP-1 population was largely outside federal programs. Bridge puts Medicare Part D
beneficiaries into exactly the population these partners serve — which is the campaign's
own central selling point. The same fact that makes the pitch compelling is the fact that
pulls the compensation structure into federal scope.

**Required before launch:**

- [ ] Healthcare regulatory counsel reviews the provider compensation structure against AKS,
      EKRA, Stark and state law — **in writing**
- [ ] Written guidance on whether federal-beneficiary patients must be carved out of the
      provider-earning model, and how that carve-out is operationalized
- [ ] Sales talk-track approved for "what do we make on it?" — see `messaging.md` §6
- [ ] Reps instructed: **never quote, estimate or model provider earnings.** Pricing is
      volume-tiered and quoted by the team, and earnings language is exactly where this risk
      lives.

Motion B (Enterprise & Wholesale — volume purchase at tiered pricing, no per-referral
compensation) does not carry the same exposure. **If counsel restricts Motion A, the campaign
still runs on Motion B.** Sequences are written so the two motions are separable.

Nothing here is legal advice, and this list is not exhaustive. Route it to counsel.

---

## 1c. New York

The GLP-1 test is **temporarily unavailable in NY state**.

- Suppress NY-only organizations at the **list** stage, not the send stage.
- For multi-state prospects, disclose the limitation on the first call — do not let them
  discover it at contracting.
- Never imply nationwide availability without the carve-out.

---

## 2. Claim substantiation (FTC)

The FTC's Health Products Compliance Guidance requires competent and reliable scientific
evidence for health-related claims, and it applies to B2B marketing, not just consumer ads.

- **Every number in outbound copy must trace to a cited, verifiable source.** If it is a
  benchmark rather than our own result, label it as a benchmark.
- **No efficacy or outcome claims** about weight loss, adherence, or clinical results —
  ours or a customer's — without written substantiation on file.
- **Customer results are case studies, not promises.** Named, with written permission,
  with the actual conditions stated. No "typical results" framing.
- **Do not repeat a prospect's own claims back as fact.** If a prospect says their program
  produces X, that is their claim to substantiate, not ours to amplify.
- **`[PLACEHOLDER]` markers in sequence copy are load-bearing.** Any bracketed statistic
  in `../sequences.md` must be replaced with a sourced figure or deleted before launch. Do
  not ship a placeholder.
- **Product facts are safe; economics are not.** Everything marked ✅ in `messaging.md` §3
  is on the live landing page and may be stated verbatim. The blocked rows (P19 partner
  earnings, P20 activation/retention lift, P21 named references) may not appear in outbound
  in any form, including "typical," "up to," or a range.

---

## 3. No PHI, ever

HIPAA is the prospect's obligation more than ours in a prospecting context, but a single
mistake here is unrecoverable.

- Never reference an individual patient, member, or their health information in outreach.
- Never ask a prospect to send patient data during discovery, in any format, including
  "anonymized" samples. Sample data requests happen after a BAA is executed, through the
  agreed channel.
- Business contact data only in the CRM: name, title, company, work email, work phone.
- If a prospect volunteers PHI in a reply, do not copy it into the CRM, the dashboard, or a
  ticket. Note that it was received and escalate to the privacy owner.
- A **BAA must be executed** before any integration work touching patient data begins.

---

## 4. Email — CAN-SPAM and friends

Every commercial email in this campaign must have:

- [ ] Accurate, non-deceptive **From**, **Reply-To**, and routing headers
- [ ] A subject line that reflects the actual content
- [ ] A **valid physical postal address**
- [ ] A **clear, functional opt-out** in every message, honored **within 10 business days**
- [ ] No opt-out fee, no information required beyond the email address
- [ ] Identification as an advertisement where the relationship isn't already established

**Beyond the US:**

| Jurisdiction | Rule |
|---|---|
| **Canada (CASL)** | Consent-based. Only send under a documented express or implied consent basis (an existing business relationship, or a conspicuously published business address relevant to the recipient's role). Penalties are severe — when in doubt, don't. |
| **EU/UK (GDPR)** | Legitimate-interest basis must be documented before sending, with a balancing test on file. Honor access and erasure requests within 30 days. |
| **US states** | Several state privacy laws now carry their own deletion/opt-out obligations. Route requests through one intake, not per-rep. |

**Suppression is global and immediate.** One suppression list across every channel and
every rep. An opt-out on LinkedIn suppresses the email track too, and vice versa. Add
competitors, current customers, active opportunities, and anyone who has asked us to stop.

---

## 5. LinkedIn automation — read this before configuring Dripify

**This is a genuine risk, not a formality.**

LinkedIn's User Agreement prohibits using bots or other automated methods to access the
service. Cloud-based automation tools — Dripify among them — operate against that
prohibition regardless of how carefully they are configured. LinkedIn enforces with
warnings, feature restrictions, and permanent account bans. The account at risk is the
rep's personal professional identity, which the company cannot replace.

**If we proceed anyway, these limits are mandatory:**

| Control | Limit |
|---|---|
| Connection requests | ≤ 20/day/account, ramped from 5 over two weeks |
| Messages (1st-degree) | ≤ 40/day/account |
| Profile views | ≤ 60/day/account |
| Activity window | Business hours in the rep's stated timezone only, with randomized intervals |
| Account age | No automation on accounts younger than 6 months or with <500 connections |
| Withdrawal | Withdraw unaccepted invites after 21 days to protect acceptance ratio |
| Tier 1 (S2, S6) | **No automation at all** — enterprise personas are manually messaged |

**The safer alternatives, in order of preference:**

1. **LinkedIn Sales Navigator + manual sends.** Slower, zero ToS exposure, materially
   better acceptance rates on enterprise personas. This is the recommended path for Tier 1.
2. **Email-primary with LinkedIn used only for research and manual touches.** Gets most of
   the multichannel lift with none of the automation risk.
3. **LinkedIn's own advertising products** (Message Ads, Conversation Ads) — paid,
   sanctioned, and the only mechanically safe way to reach volume in-platform.

**Recommendation:** run S1/S3/S4/S5 on the email-primary sequence with manual LinkedIn
touches, and reserve automation — if the business accepts the risk in writing — for S1
only, where the account-value-to-risk ratio is least bad. The dashboard in this directory
is channel-agnostic and works with any of these.

---

## 6. Segment-specific care

- **Pharmacies (S4):** state boards regulate pharmacy advertising and, in some states, the
  solicitation of pharmacist relationships. Do not imply any dispensing partnership.
- **Employers/TPAs (S6):** procurement rules may forbid direct outreach to benefits staff
  during an open RFP. Check for an active RFP before sequencing a named account.
- **Clinics (S1, S2):** never suggest a specific clinical protocol, testing cadence, or
  prescribing decision. We describe what our panels measure; their medical director decides
  what to order and when. Crossing this line invites both corporate-practice-of-medicine
  and product-liability exposure.
- **Gyms (S5):** avoid any framing that positions a fitness operator as delivering medical
  care. The clinical decision sits with their licensed provider partner.

---

## 7. Pre-launch checklist

- [ ] **Healthcare regulatory counsel has signed off on the provider compensation structure (§1b)**
- [ ] **Decision recorded on whether Motion A launches, or the campaign runs Motion B only (§1b)**
- [ ] **NY-only organizations suppressed at the list stage (§1c)**
- [ ] No message quotes, estimates or models partner earnings
- [ ] Counsel has reviewed every sequence in `../sequences.md`
- [ ] Every `[PLACEHOLDER]` replaced with a sourced figure or removed
- [ ] No branded drug names anywhere in the copy
- [ ] No supply/prescribing/access implication anywhere in the copy
- [ ] Physical address and working unsubscribe in every email template
- [ ] Suppression list loaded and shared across all channels and reps
- [ ] Sending domain authenticated: SPF, DKIM, DMARC — on a subdomain, not the root domain
- [ ] Domain warmed for 3+ weeks before volume sending
- [ ] CASL/GDPR basis documented for every non-US contact, or non-US contacts excluded
- [ ] LinkedIn automation decision made **in writing** by an accountable owner (§5)
- [ ] Landing page claims match the sequence claims, and both are substantiated
- [ ] Privacy request intake exists and is staffed
- [ ] Reps briefed on the PHI rule (§3) and the no-protocol-advice rule (§6)

---

## 8. Escalate, don't improvise

Stop and route to the compliance owner when a prospect:

- asks us to supply, source, or broker medication
- asks us to recommend a testing protocol or a prescribing decision
- sends PHI
- asks us to ship to a state where we are not licensed
- raises a regulatory action against their own business
- asks us to make a claim we cannot substantiate
