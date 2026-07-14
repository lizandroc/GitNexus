/* Minimal node test runner for the QuillCheck engine. Run: npm test */
const assert = require('assert');
const { checkText, matchCase, countSyllables, detectTone } = require('../renderer/engine.js');

let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    passed++;
    console.log('  ✓ ' + name);
  } catch (err) {
    failed++;
    console.error('  ✗ ' + name);
    console.error('    ' + err.message);
  }
}

function rulesIn(text) {
  return checkText(text).issues.map(i => i.rule);
}

function findIssue(text, rule) {
  return checkText(text).issues.find(i => i.rule === rule);
}

console.log('QuillCheck engine tests\n');

test('flags common misspellings with cased correction', () => {
  const iss = findIssue('Teh cat sat.', 'spelling');
  assert.ok(iss, 'expected a spelling issue');
  assert.strictEqual(iss.suggestions[0], 'The');
});

test('flags "could of" style grammar errors', () => {
  const iss = findIssue('I could of gone home.', 'grammar');
  assert.ok(iss);
  assert.strictEqual(iss.suggestions[0], 'could have');
});

test('flags repeated words', () => {
  const iss = findIssue('This is the the end.', 'repeated-word');
  assert.ok(iss);
  assert.strictEqual(iss.suggestions[0], 'the');
});

test('a/an: flags "a apple" and suggests "an"', () => {
  const iss = findIssue('She ate a apple.', 'article');
  assert.ok(iss);
  assert.strictEqual(iss.suggestions[0], 'an');
});

test('a/an: accepts "a university" and "an hour"', () => {
  assert.ok(!findIssue('He attends a university.', 'article'));
  assert.ok(!findIssue('Wait an hour.', 'article'));
});

test('flags double spaces but not indentation', () => {
  assert.ok(findIssue('Hello  world.', 'spacing'));
  assert.ok(!findIssue('line one\n  indented line', 'spacing'));
});

test('flags missing space after punctuation', () => {
  const iss = findIssue('Hello,world.', 'spacing');
  assert.ok(iss);
  assert.strictEqual(iss.suggestions[0], ', ');
});

test('flags lowercase standalone "i"', () => {
  const iss = findIssue('Yesterday i went home.', 'capitalization');
  assert.ok(iss);
  assert.strictEqual(iss.suggestions[0], 'I');
});

test('flags uncapitalized sentence starts', () => {
  const iss = findIssue('Good morning. the sun is out.', 'capitalization');
  assert.ok(iss);
  assert.strictEqual(iss.suggestions[0], 'T');
});

test('flags filler words as clarity issues', () => {
  const iss = findIssue('This is very good.', 'filler');
  assert.ok(iss);
  assert.strictEqual(iss.category, 'clarity');
});

test('flags passive voice as engagement', () => {
  const iss = findIssue('The ball was thrown by the boy. It was kicked hard.', 'passive-voice');
  assert.ok(iss);
  assert.strictEqual(iss.category, 'engagement');
});

test('flags sentences over 30 words', () => {
  const long = 'This sentence goes on and on and on because it contains far too many words for anyone to comfortably read without pausing several times along the way to catch a breath somewhere.';
  assert.ok(findIssue(long, 'long-sentence'));
});

test('clean text yields no issues and score 100', () => {
  const { issues, stats } = checkText('The quick brown fox jumps over a dog.');
  assert.strictEqual(issues.length, 0);
  assert.strictEqual(stats.score, 100);
});

test('empty text yields score 100 and zero counts', () => {
  const { issues, stats } = checkText('');
  assert.strictEqual(issues.length, 0);
  assert.strictEqual(stats.words, 0);
  assert.strictEqual(stats.score, 100);
});

test('stats count words and sentences', () => {
  const { stats } = checkText('One two three. Four five six!');
  assert.strictEqual(stats.words, 6);
  assert.strictEqual(stats.sentences, 2);
});

test('issues are sorted by position with no exact duplicates', () => {
  const { issues } = checkText('teh teh cat i saw.');
  for (let k = 1; k < issues.length; k++) {
    assert.ok(issues[k].start >= issues[k - 1].start, 'issues out of order');
  }
  const keys = issues.map(i => i.start + ':' + i.end + ':' + i.rule);
  assert.strictEqual(new Set(keys).size, keys.length, 'duplicate issues');
});

test('matchCase preserves capitalization styles', () => {
  assert.strictEqual(matchCase('Teh', 'the'), 'The');
  assert.strictEqual(matchCase('TEH', 'the'), 'THE');
  assert.strictEqual(matchCase('teh', 'the'), 'the');
});

test('countSyllables gives sane values', () => {
  assert.strictEqual(countSyllables('cat'), 1);
  assert.ok(countSyllables('beautiful') >= 3);
});

test('detectTone labels formal and friendly text', () => {
  assert.strictEqual(
    detectTone('Furthermore, the committee has decided. Therefore, the motion carries.'),
    'Formal'
  );
  assert.strictEqual(
    detectTone('Thanks so much! This is awesome! Love it!'),
    'Friendly'
  );
});

console.log('\n' + passed + ' passed, ' + failed + ' failed');
process.exit(failed ? 1 : 0);
