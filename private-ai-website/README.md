# Sovereign AI Systems — Company Website

A conversion-focused enterprise landing page for a private AI infrastructure company. Built with **Next.js 14 (App Router) + React 18 + Tailwind CSS 3**, fully responsive, SEO-ready, with a working contact form API route.

> Branding is a placeholder ("Sovereign AI Systems"). Swap the name in `components/Navbar.tsx`, `components/Footer.tsx`, and `app/layout.tsx`, and set your real domain in `metadataBase`.

## Setup

```bash
cd private-ai-website
npm install
```

## Run

```bash
npm run dev        # development — http://localhost:3000
npm run build      # production build
npm run start      # serve the production build
```

## Structure

```
app/
  layout.tsx            # SEO metadata (title template, OG, Twitter, robots)
  page.tsx              # section composition — the whole page in one glance
  globals.css           # Tailwind + shared component classes (btn, card, field…)
  api/contact/route.ts  # contact form endpoint (validates, logs; swap in email/CRM)
components/
  Section.tsx           # shared section shell (label / title / lead / spacing)
  Icon.tsx              # inline SVG icon set (no icon library dependency)
  Navbar.tsx            # sticky nav + mobile menu (client component)
  Hero.tsx  Problem.tsx  Solution.tsx  UseCases.tsx  HowItWorks.tsx
  PrivacyControl.tsx  Technology.tsx  Benefits.tsx  Packages.tsx
  About.tsx  FinalCTA.tsx  ContactSection.tsx  ContactForm.tsx  Footer.tsx
tailwind.config.ts      # ink/brand/mist palette — retheme in one place
```

## Page sections (in order)

Hero → Problem → Solution (3 pillars) → Use Cases (12) → How It Works (6 steps) → Privacy & Control (8 guarantees + honesty note) → Technology (plain-English) → Enterprise Benefits → Engagements (3 tiers) → About/Credibility → Final CTA → Contact form → Footer.

## Contact form

The frontend (`components/ContactForm.tsx`) collects: name, company, email, phone, industry, what they want AI to help with, local/private deployment need, and timeline. It POSTs JSON to `/api/contact`, which validates and currently logs the inquiry server-side.

**To receive inquiries for real**, replace the `deliver()` function in `app/api/contact/route.ts` with your destination — e.g. Resend/SES/Postmark email, a CRM webhook, or a database insert. Nothing else needs to change.

## Deployment

Any Node host works: `npm run build && npm run start` behind a reverse proxy, or deploy to Vercel/Netlify as-is (the contact API route runs as a serverless function).

## Future improvements

- Book-a-call integration (Cal.com or Calendly embed) on the primary CTA
- Case studies / client logos section once references exist
- Blog or insights section for SEO (App Router `app/insights/`)
- Email delivery + spam protection (honeypot field, rate limiting) on the contact API
- Analytics with a privacy-respecting tool (Plausible/Fathom) to match the brand promise
- Light-theme variant and `prefers-color-scheme` support
- OG image generation (`opengraph-image.tsx`) for richer link previews
