/**
 * Partner-inquiry intake for mylabboxweightloss.com
 *
 * The landing page ships as a static Claude Design export whose submit handler is:
 *
 *     handleSubmit: (e) => { e.preventDefault(); this.setState({ submitted: true }); }
 *
 * It shows "Thanks — we've got it!" and discards the submission. This Worker is the
 * endpoint that makes the form real. It validates the payload, classifies it against the
 * campaign ICP (so an inquiry arrives already segmented and scored), persists it, and
 * optionally notifies by email and/or webhook.
 *
 * Deploy: see ../README.md
 */

const ORG_TYPES = {
  'Medical weight loss clinic': { segment: 'S1', motion: 'A', tier: 3, sequence: 'SEQ-A' },
  'Telehealth platform': { segment: 'S2', motion: 'A/B', tier: 2, sequence: 'SEQ-B' },
  Pharmacy: { segment: 'S3', motion: 'B', tier: 2, sequence: 'SEQ-B' },
  'Employer / benefits program': { segment: 'S4', motion: 'B', tier: 1, sequence: 'SEQ-C' },
  'Health system': { segment: 'S5', motion: 'B', tier: 1, sequence: 'SEQ-C' },
  Other: { segment: 'S6', motion: 'B', tier: 2, sequence: 'SEQ-B' },
};

// Q2 in strategy/icp-and-segments.md scores off the form's own volume bands.
const VOLUME_SCORE = {
  '500+ kits': 2,
  '100–500 kits': 2,
  '25–100 kits': 1,
  'Under 25 kits': 0,
};

const MAX_BODY = 16 * 1024;
const MAX_PER_IP_PER_HOUR = 8;

const cors = (origin, allowed) => ({
  'Access-Control-Allow-Origin': allowed.includes(origin) ? origin : allowed[0],
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Max-Age': '86400',
  Vary: 'Origin',
});

const json = (body, status, headers) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json', ...headers },
  });

const str = (v, max) =>
  typeof v === 'string' ? v.trim().slice(0, max) : v == null ? '' : String(v).trim().slice(0, max);

// Deliberately permissive: reject only what is clearly not an address. Over-strict regexes
// bounce real addresses, and a lost partner inquiry is the exact failure being fixed here.
const EMAIL_RE = /^[^\s@,;<>()[\]\\]+@[^\s@,;<>()[\]\\]+\.[A-Za-z]{2,}$/;

function classify(orgType, volume) {
  const org = ORG_TYPES[orgType] || ORG_TYPES.Other;
  const volumeScore = VOLUME_SCORE[volume] ?? 0;
  // Tier 1 and a 100+ kit band are the two signals available at form time; everything else
  // in the MEDDIC-lite scorecard needs a human on a call.
  const score = volumeScore + (org.tier === 1 ? 2 : org.tier === 2 ? 1 : 0);
  return {
    ...org,
    volumeScore,
    intakeScore: score,
    priority: score >= 3 ? 'high' : score >= 2 ? 'medium' : 'low',
  };
}

async function rateLimited(env, ip) {
  if (!env.INQUIRIES || !ip) return false;
  const key = `rl:${ip}:${new Date().toISOString().slice(0, 13)}`;
  const n = Number((await env.INQUIRIES.get(key)) || 0);
  if (n >= MAX_PER_IP_PER_HOUR) return true;
  await env.INQUIRIES.put(key, String(n + 1), { expirationTtl: 7200 });
  return false;
}

async function notifyEmail(env, rec) {
  if (!env.RESEND_API_KEY || !env.NOTIFY_TO) return;
  const line = (k, v) =>
    `<tr><td style="padding:4px 12px 4px 0"><b>${k}</b></td><td>${v}</td></tr>`;
  const esc = (s) =>
    String(s).replace(
      /[&<>"']/g,
      (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c],
    );
  await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      from: env.NOTIFY_FROM || 'inquiries@mylabboxweightloss.com',
      to: env.NOTIFY_TO.split(',').map((s) => s.trim()),
      reply_to: rec.email,
      subject: `[${rec.priority.toUpperCase()}] ${rec.orgType} — ${rec.organization}`,
      html: `<h2>New partner inquiry</h2><table style="font:14px system-ui">
${line('Name', esc(rec.name))}
${line('Email', esc(rec.email))}
${line('Organization', esc(rec.organization))}
${line('Phone', esc(rec.phone || '—'))}
${line('Org type', esc(rec.orgType))}
${line('Monthly volume', esc(rec.volume || '—'))}
${line('Segment', `${rec.segment} · Motion ${rec.motion} · Tier ${rec.tier} · ${rec.sequence}`)}
${line('Intake score', `${rec.intakeScore} (${rec.priority})`)}
</table>
<p><b>Notes</b><br>${esc(rec.notes || '—')}</p>
<p style="color:#b45309"><b>Before replying:</b> confirm which states they operate in — the
GLP-1 panel is temporarily unavailable in NY. Motion A (provider partnership) is gated on
the anti-kickback review; if that has not cleared, respond on Motion B terms only.</p>`,
    }),
  }).catch(() => {});
}

export default {
  async fetch(request, env, ctx) {
    const allowed = (env.ALLOWED_ORIGINS || 'https://mylabboxweightloss.com')
      .split(',')
      .map((s) => s.trim());
    const origin = request.headers.get('Origin') || '';
    const headers = cors(origin, allowed);

    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers });
    if (request.method !== 'POST') return json({ ok: false, error: 'method' }, 405, headers);
    if (origin && !allowed.includes(origin))
      return json({ ok: false, error: 'origin' }, 403, headers);

    const raw = await request.text();
    if (raw.length > MAX_BODY) return json({ ok: false, error: 'too_large' }, 413, headers);

    let body;
    try {
      body = JSON.parse(raw);
    } catch {
      return json({ ok: false, error: 'bad_json' }, 400, headers);
    }

    // Honeypot: injected by the client script and invisible to humans. Accept-and-drop so a
    // bot sees success and does not retune.
    if (str(body.company_website, 200)) return json({ ok: true, id: 'ok' }, 200, headers);

    const ip = request.headers.get('CF-Connecting-IP') || '';
    if (await rateLimited(env, ip)) return json({ ok: false, error: 'rate_limited' }, 429, headers);

    const name = str(body.name, 200);
    const email = str(body.email, 320);
    const organization = str(body.organization, 200);
    const orgType = str(body.orgType, 100);

    const missing = [];
    if (!name) missing.push('name');
    if (!email) missing.push('email');
    if (!organization) missing.push('organization');
    if (!orgType || orgType.startsWith('Select')) missing.push('orgType');
    if (missing.length) return json({ ok: false, error: 'missing', fields: missing }, 400, headers);
    if (!EMAIL_RE.test(email)) return json({ ok: false, error: 'bad_email' }, 400, headers);

    const volume = str(body.volume, 60);
    const rec = {
      id: crypto.randomUUID(),
      receivedAt: new Date().toISOString(),
      name,
      email,
      organization,
      phone: str(body.phone, 60),
      orgType,
      volume: volume.startsWith('Select') ? '' : volume,
      notes: str(body.notes, 4000),
      ...classify(orgType, volume),
      source: str(body.source, 200) || 'mylabboxweightloss.com',
      // Not derivable from the form as it stands — there is no state field. Confirm on the
      // first call; the panel is temporarily unavailable in NY.
      nyCheckRequired: true,
      stage: 'Inbound',
      country: request.headers.get('CF-IPCountry') || '',
      userAgent: str(request.headers.get('User-Agent'), 300),
    };

    if (env.INQUIRIES) {
      await env.INQUIRIES.put(`inquiry:${rec.receivedAt}:${rec.id}`, JSON.stringify(rec));
    }

    const after = [notifyEmail(env, rec)];
    if (env.WEBHOOK_URL) {
      after.push(
        fetch(env.WEBHOOK_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(rec),
        }).catch(() => {}),
      );
    }
    ctx.waitUntil(Promise.all(after));

    return json(
      { ok: true, id: rec.id, segment: rec.segment, priority: rec.priority },
      200,
      headers,
    );
  },
};
