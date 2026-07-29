#!/usr/bin/env node
/**
 * Inlines data/campaign.json into dashboard.template.html and writes dashboard.html.
 *
 * The dashboard has to be a single self-contained file — it is published as an artifact
 * and opened straight off disk, so it can't fetch its data at runtime. This keeps
 * campaign.json as the one source of truth and regenerates the page from it.
 *
 *   node build.mjs
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const MARKER = '<!--CAMPAIGN_DATA-->';

const raw = readFileSync(join(here, 'data/campaign.json'), 'utf8');
const data = JSON.parse(raw); // fail loudly on malformed JSON

// Guard the totals the dashboard presents as facts about itself.
const sum = (k) => data.segments.reduce((t, s) => t + s[k], 0);
const funnel = Object.fromEntries(data.funnel.map((f) => [f.stage, f.value]));
const checks = [
  ['funnel Sourced', funnel.Sourced, sum('sourced')],
  ['funnel Contacted', funnel.Contacted, sum('contacted')],
  ['funnel Engaged', funnel.Engaged, sum('engaged')],
  ['funnel Replied', funnel.Replied, sum('replied')],
  ['funnel Meeting', funnel.Meeting, sum('meetings')],
  ['weekly contacted', data.weekly.reduce((t, w) => t + w.contacted, 0), sum('contacted')],
  ['weekly replied', data.weekly.reduce((t, w) => t + w.replied, 0), sum('replied')],
  ['weekly meetings', data.weekly.reduce((t, w) => t + w.meetings, 0), sum('meetings')],
];
const bad = checks.filter(([, a, b]) => a !== b);
if (bad.length) {
  console.error('campaign.json totals do not reconcile:');
  for (const [name, a, b] of bad) console.error(`  ${name}: ${a} != segment sum ${b}`);
  process.exit(1);
}

const segIds = new Set(data.segments.map((s) => s.id));
const seqIds = new Set(data.sequences.map((s) => s.id));
for (const l of data.leads) {
  if (!segIds.has(l.segment))
    throw new Error(`lead "${l.account}" has unknown segment ${l.segment}`);
  if (!seqIds.has(l.sequence))
    throw new Error(`lead "${l.account}" has unknown sequence ${l.sequence}`);
}

const tpl = readFileSync(join(here, 'dashboard.template.html'), 'utf8');
if (!tpl.includes(MARKER)) throw new Error(`template is missing ${MARKER}`);

// Escape only what could terminate the host <script> element.
const payload = JSON.stringify(data)
  .replace(/<\/script/gi, '<\\/script')
  .replace(/<!--/g, '<\\!--');

writeFileSync(join(here, 'dashboard.html'), tpl.replace(MARKER, payload), 'utf8');
console.log(
  `dashboard.html written — ${data.segments.length} segments, ${data.sequences.length} sequences, ${data.leads.length} sample accounts`,
);
