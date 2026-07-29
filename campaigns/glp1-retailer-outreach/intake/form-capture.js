/**
 * Partner-inquiry form capture for mylabboxweightloss.com
 *
 * The landing page is a static Claude Design export. Its submit handler calls
 * preventDefault(), flips to "Thanks — we've got it!", and discards the data — so every
 * inquiry is currently lost while the prospect believes they have reached you.
 *
 * This script attaches at the document level in the CAPTURE phase, so it reads the fields
 * before the page's own handler swallows the event, and it does not depend on the bundler's
 * internals or on when the form is rendered. Nothing about the page's look or behaviour
 * changes: the visitor still sees the same confirmation.
 *
 * The form's inputs have no name attributes, so fields are matched by their visible label.
 *
 * Install: set ENDPOINT below, then add before </body> in index.html:
 *   <script src="form-capture.js" defer></script>
 * (or paste the contents inline inside a <script> tag).
 */
(function () {
  'use strict';

  var ENDPOINT = 'https://REPLACE-ME.workers.dev'; // ← your deployed Worker URL
  var QUEUE_KEY = 'mlb_inquiry_queue_v1';

  // Visible label text -> payload key. Matched on a normalised prefix, so trailing
  // asterisks and punctuation on the page don't have to be mirrored here.
  var FIELDS = [
    ['full name', 'name'],
    ['work email', 'email'],
    ['organization type', 'orgType'], // must precede "organization"
    ['organization', 'organization'],
    ['phone', 'phone'],
    ['estimated monthly volume', 'volume'],
    ['anything else', 'notes'],
  ];

  var norm = function (s) {
    return String(s || '')
      .replace(/\s+/g, ' ')
      .trim()
      .toLowerCase();
  };

  function keyForLabel(text) {
    var t = norm(text)
      .replace(/[*:?]+$/, '')
      .trim();
    for (var i = 0; i < FIELDS.length; i++) {
      if (t.indexOf(FIELDS[i][0]) === 0) return FIELDS[i][1];
    }
    return null;
  }

  /* Walk the form in document order; each control belongs to the most recent label. */
  function readForm(form) {
    var out = {};
    var nodes = form.querySelectorAll('label, input, select, textarea');
    var pending = null;
    for (var i = 0; i < nodes.length; i++) {
      var n = nodes[i];
      if (n.tagName === 'LABEL') {
        pending = keyForLabel(n.textContent);
        continue;
      }
      if (n.type === 'hidden' || n.name === 'company_website') continue;
      if (pending) {
        out[pending] = (n.value || '').trim();
        pending = null;
      }
    }
    return out;
  }

  function addHoneypot(form) {
    if (form.querySelector('input[name="company_website"]')) return;
    var hp = document.createElement('input');
    hp.type = 'text';
    hp.name = 'company_website';
    hp.tabIndex = -1;
    hp.autocomplete = 'off';
    hp.setAttribute('aria-hidden', 'true');
    hp.style.cssText =
      'position:absolute;left:-9999px;width:1px;height:1px;opacity:0;pointer-events:none';
    form.appendChild(hp);
  }

  function readQueue() {
    try {
      var q = JSON.parse(localStorage.getItem(QUEUE_KEY) || '[]');
      return Array.isArray(q) ? q : [];
    } catch (e) {
      return [];
    }
  }
  function writeQueue(q) {
    try {
      localStorage.setItem(QUEUE_KEY, JSON.stringify(q.slice(-20)));
    } catch (e) {
      /* storage full or blocked — the send below is still attempted */
    }
  }

  function post(payload) {
    return fetch(ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
      keepalive: true, // survives the page being closed right after submit
    }).then(function (r) {
      if (!r.ok && r.status >= 500) throw new Error('server ' + r.status);
      return r;
    });
  }

  /* A submission that fails to send is held locally and retried on the next page load,
     rather than being dropped after the visitor has already been told it went through. */
  function send(payload) {
    post(payload).catch(function () {
      var q = readQueue();
      q.push(payload);
      writeQueue(q);
    });
  }

  function flushQueue() {
    var q = readQueue();
    if (!q.length) return;
    writeQueue([]);
    q.forEach(function (item) {
      send(item);
    });
  }

  document.addEventListener(
    'submit',
    function (e) {
      var form = e.target;
      if (!form || form.tagName !== 'FORM') return;
      var data = readForm(form);
      if (!data.email && !data.organization) return; // not the inquiry form
      var hp = form.querySelector('input[name="company_website"]');
      data.company_website = hp ? hp.value : '';
      data.source = location.href;
      data.submittedAt = new Date().toISOString();
      send(data);
    },
    true, // capture: run before the page's own preventDefault handler
  );

  /* The form is rendered asynchronously by the page's bundler, so watch for it. */
  function scan() {
    var forms = document.querySelectorAll('form');
    for (var i = 0; i < forms.length; i++) addHoneypot(forms[i]);
  }
  if (document.readyState !== 'loading') scan();
  document.addEventListener('DOMContentLoaded', scan);
  new MutationObserver(scan).observe(document.documentElement, { childList: true, subtree: true });
  flushQueue();
})();
