/* QuillCheck renderer — wires the engine to the editor UI. */
(function () {
  'use strict';

  const editor = document.getElementById('editor');
  const backdrop = document.getElementById('backdrop');
  const cardsEl = document.getElementById('cards');
  const emptyState = document.getElementById('emptyState');
  const scoreNum = document.getElementById('scoreNum');
  const scoreRing = document.getElementById('scoreRing');
  const toneChip = document.getElementById('toneChip');
  const filtersEl = document.getElementById('filters');

  const RING_CIRC = 100.5; // matches stroke-dasharray in CSS

  let issues = [];
  let activeFilter = 'all';
  let selectedIndex = -1;
  // Dismissals survive re-checks: keyed by rule + the exact flagged text.
  const dismissed = new Set();

  const debounce = (fn, ms) => {
    let t;
    return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
  };

  function escapeHtml(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function dismissKey(text, iss) {
    return iss.rule + '|' + text.slice(iss.start, iss.end);
  }

  // ---- Analysis --------------------------------------------------------

  function analyze() {
    const text = editor.value;
    const result = QuillEngine.checkText(text);
    issues = result.issues.filter(i => !dismissed.has(dismissKey(text, i)));
    renderHighlights(text);
    renderCards(text);
    renderStats(result.stats);
  }

  const analyzeDebounced = debounce(analyze, 250);

  // ---- Highlights ------------------------------------------------------

  function renderHighlights(text) {
    let html = '';
    let pos = 0;
    // Issues are sorted; skip overlaps so marks never nest.
    for (let k = 0; k < issues.length; k++) {
      const i = issues[k];
      if (i.start < pos) continue;
      html += escapeHtml(text.slice(pos, i.start));
      const cls = i.category + (k === selectedIndex ? ' active-issue' : '');
      html += '<mark class="' + cls + '">' + escapeHtml(text.slice(i.start, i.end)) + '</mark>';
      pos = i.end;
    }
    html += escapeHtml(text.slice(pos));
    // Trailing newline needs a filler char so the backdrop matches textarea height
    backdrop.innerHTML = html + '\n';
    syncScroll();
  }

  function syncScroll() {
    backdrop.scrollTop = editor.scrollTop;
    backdrop.scrollLeft = editor.scrollLeft;
  }

  // ---- Sidebar cards ---------------------------------------------------

  function excerptFor(text, iss) {
    const flagged = text.slice(iss.start, iss.end);
    const fix = iss.suggestions[0];
    if (fix !== undefined && fix !== '' && iss.suggestions.length) {
      return '<s>' + escapeHtml(flagged) + '</s> → <span class="fix">' + escapeHtml(fix) + '</span>';
    }
    if (fix === '') {
      return '<s>' + escapeHtml(flagged) + '</s> <span class="fix">(remove)</span>';
    }
    const short = flagged.length > 60 ? flagged.slice(0, 57) + '…' : flagged;
    return '“' + escapeHtml(short) + '”';
  }

  function renderCards(text) {
    const visible = issues
      .map((iss, idx) => ({ iss, idx }))
      .filter(({ iss }) => activeFilter === 'all' || iss.category === activeFilter);

    // Counts
    const counts = { all: issues.length, correctness: 0, clarity: 0, engagement: 0 };
    for (const i of issues) if (counts[i.category] !== undefined) counts[i.category]++;
    document.getElementById('countAll').textContent = counts.all;
    document.getElementById('countCorrectness').textContent = counts.correctness;
    document.getElementById('countClarity').textContent = counts.clarity;
    document.getElementById('countEngagement').textContent = counts.engagement;

    cardsEl.querySelectorAll('.card').forEach(c => c.remove());
    emptyState.style.display = visible.length ? 'none' : '';

    for (const { iss, idx } of visible) {
      const card = document.createElement('div');
      card.className = 'card' + (idx === selectedIndex ? ' selected' : '');
      card.innerHTML =
        '<div class="card-top"><span class="dot ' + iss.category + '"></span>' +
        '<span class="card-cat">' + iss.category + '</span></div>' +
        '<div class="card-excerpt">' + excerptFor(text, iss) + '</div>' +
        '<div class="card-msg">' + escapeHtml(iss.message) + '</div>' +
        '<div class="card-actions">' +
        (iss.suggestions.length ? '<button class="btn btn-apply">Apply</button>' : '') +
        '<button class="btn btn-dismiss">Dismiss</button></div>';

      card.addEventListener('click', () => selectIssue(idx));
      const applyBtn = card.querySelector('.btn-apply');
      if (applyBtn) applyBtn.addEventListener('click', e => { e.stopPropagation(); applyFix(idx); });
      card.querySelector('.btn-dismiss').addEventListener('click', e => { e.stopPropagation(); dismissIssue(idx); });
      cardsEl.appendChild(card);
    }
  }

  function selectIssue(idx) {
    selectedIndex = idx;
    const iss = issues[idx];
    renderHighlights(editor.value);
    renderCards(editor.value);
    if (iss) {
      editor.focus();
      editor.setSelectionRange(iss.start, iss.end);
      // Rough scroll-into-view: put caret line near the middle
      const before = editor.value.slice(0, iss.start);
      const line = before.split('\n').length;
      const lineHeight = 17 * 1.7;
      editor.scrollTop = Math.max(0, line * lineHeight - editor.clientHeight / 2);
      syncScroll();
    }
  }

  function applyFix(idx) {
    const iss = issues[idx];
    if (!iss || !iss.suggestions.length) return;
    let replacement = iss.suggestions[0];
    let { start, end } = iss;
    // Removing a filler word: also swallow one following space
    if (replacement === '') {
      if (editor.value[end] === ' ') end++;
      else if (editor.value[start - 1] === ' ') start--;
    }
    editor.setRangeText(replacement, start, end, 'end');
    selectedIndex = -1;
    analyze();
    editor.focus();
  }

  function dismissIssue(idx) {
    const iss = issues[idx];
    if (!iss) return;
    dismissed.add(dismissKey(editor.value, iss));
    selectedIndex = -1;
    analyze();
  }

  // ---- Stats + score ---------------------------------------------------

  function renderStats(stats) {
    document.getElementById('statWords').textContent = stats.words + ' words';
    document.getElementById('statChars').textContent = stats.characters + ' characters';
    document.getElementById('statSentences').textContent = stats.sentences + ' sentences';
    document.getElementById('statTime').textContent =
      stats.readingTimeSec < 60
        ? stats.readingTimeSec + ' sec read'
        : Math.round(stats.readingTimeSec / 60) + ' min read';
    document.getElementById('statReadability').textContent =
      stats.words ? 'Readability ' + stats.readability : 'Readability —';

    scoreNum.textContent = stats.score;
    scoreRing.style.strokeDashoffset = RING_CIRC * (1 - stats.score / 100);
    scoreRing.style.stroke =
      stats.score >= 80 ? 'var(--green)' : stats.score >= 50 ? '#f2b824' : 'var(--red)';
    toneChip.textContent = stats.tone;
  }

  // ---- Filters ---------------------------------------------------------

  filtersEl.addEventListener('click', e => {
    const btn = e.target.closest('.filter');
    if (!btn) return;
    activeFilter = btn.dataset.cat;
    filtersEl.querySelectorAll('.filter').forEach(f => f.classList.toggle('active', f === btn));
    renderCards(editor.value);
  });

  // ---- Events ----------------------------------------------------------

  editor.addEventListener('input', () => {
    selectedIndex = -1;
    analyzeDebounced();
  });
  editor.addEventListener('scroll', syncScroll);

  analyze();
})();
