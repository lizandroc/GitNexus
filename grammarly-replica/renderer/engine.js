/*
 * QuillCheck engine — rule-based writing analysis.
 * Runs in the renderer (browser) and in Node for tests, so it has no
 * DOM or Electron dependencies.
 *
 * checkText(text) -> { issues: Issue[], stats: Stats }
 * Issue: { start, end, category, rule, message, suggestions: string[] }
 * Categories mirror Grammarly's: correctness | clarity | engagement | delivery
 */

(function (root, factory) {
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = factory();
  } else {
    root.QuillEngine = factory();
  }
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';

  // Common misspellings -> corrections
  const MISSPELLINGS = {
    teh: 'the', taht: 'that', adn: 'and', nad: 'and', waht: 'what',
    thier: 'their', recieve: 'receive', recieved: 'received',
    seperate: 'separate', seperated: 'separated', seperately: 'separately',
    definately: 'definitely', defiantly: 'definitely', occured: 'occurred',
    occuring: 'occurring', untill: 'until', wich: 'which', becuase: 'because',
    beleive: 'believe', beleived: 'believed', acheive: 'achieve',
    acheived: 'achieved', accomodate: 'accommodate', accross: 'across',
    agressive: 'aggressive', apparant: 'apparent', arguement: 'argument',
    basicly: 'basically', begining: 'beginning', calender: 'calendar',
    catagory: 'category', cemetary: 'cemetery', changable: 'changeable',
    collegue: 'colleague', comming: 'coming', commitee: 'committee',
    completly: 'completely', concious: 'conscious', curiousity: 'curiosity',
    dissapoint: 'disappoint', dissapointed: 'disappointed',
    embarass: 'embarrass', embarassing: 'embarrassing',
    enviroment: 'environment', existance: 'existence', familar: 'familiar',
    finaly: 'finally', foriegn: 'foreign', freind: 'friend',
    goverment: 'government', gaurd: 'guard', happend: 'happened',
    harrass: 'harass', immediatly: 'immediately', independant: 'independent',
    interupt: 'interrupt', irregardless: 'regardless', knowlege: 'knowledge',
    liason: 'liaison', libary: 'library', lisence: 'license',
    maintainance: 'maintenance', managment: 'management', mispell: 'misspell',
    neccessary: 'necessary', necessery: 'necessary', noticable: 'noticeable',
    occassion: 'occasion', occassionally: 'occasionally', offical: 'official',
    oppurtunity: 'opportunity', paralell: 'parallel', perminent: 'permanent',
    persistant: 'persistent', posession: 'possession', prefered: 'preferred',
    probaly: 'probably', proffesional: 'professional', promiss: 'promise',
    pronounciation: 'pronunciation', publically: 'publicly', quater: 'quarter',
    questionaire: 'questionnaire', reccomend: 'recommend',
    reccommend: 'recommend', refered: 'referred', relevent: 'relevant',
    religous: 'religious', remeber: 'remember', repitition: 'repetition',
    restarant: 'restaurant', restaraunt: 'restaurant', rythm: 'rhythm',
    secretery: 'secretary', similiar: 'similar', sincerly: 'sincerely',
    succesful: 'successful', successfull: 'successful', sucess: 'success',
    supercede: 'supersede', suprise: 'surprise', tommorow: 'tomorrow',
    tounge: 'tongue', truely: 'truly', unfortunatly: 'unfortunately',
    usualy: 'usually', vaccuum: 'vacuum', vegatarian: 'vegetarian',
    vehical: 'vehicle', visable: 'visible', wierd: 'weird',
    wellcome: 'welcome', whereever: 'wherever', alot: 'a lot',
    stragety: 'strategy', strenght: 'strength', tomatos: 'tomatoes',
    potatos: 'potatoes', writting: 'writing', greatful: 'grateful',
    gratefull: 'grateful', buisness: 'business', bussiness: 'business'
  };

  // Phrase-level grammar fixes (matched case-insensitively on word boundaries)
  const PHRASE_FIXES = [
    { find: 'could of', fix: 'could have' },
    { find: 'should of', fix: 'should have' },
    { find: 'would of', fix: 'would have' },
    { find: 'must of', fix: 'must have' },
    { find: 'might of', fix: 'might have' },
    { find: "he don't", fix: "he doesn't" },
    { find: "she don't", fix: "she doesn't" },
    { find: "it don't", fix: "it doesn't" },
    { find: 'your welcome', fix: "you're welcome" },
    { find: 'less people', fix: 'fewer people' },
    { find: 'less things', fix: 'fewer things' },
    { find: 'more better', fix: 'better' },
    { find: 'most best', fix: 'best' },
    { find: 'i seen', fix: 'I saw' },
    { find: 'we was', fix: 'we were' },
    { find: 'they was', fix: 'they were' },
    { find: 'you was', fix: 'you were' }
  ];

  // Filler / weak words flagged for clarity
  const FILLERS = [
    'very', 'really', 'just', 'actually', 'basically', 'literally',
    'quite', 'simply', 'totally', 'absolutely', 'extremely'
  ];

  const FILLER_ALTERNATIVES = {
    very: 'Consider a stronger word instead of "very" (e.g. "very big" → "huge").',
    really: 'Consider removing "really" or using a more precise word.',
    just: '"Just" often weakens your message. Consider removing it.',
    actually: '"Actually" is usually unnecessary. Consider removing it.',
    basically: '"Basically" is usually unnecessary. Consider removing it.',
    literally: '"Literally" is often overused. Remove it unless meant literally.',
    quite: '"Quite" is vague. Consider a more precise word.',
    simply: '"Simply" can sound dismissive. Consider removing it.',
    totally: '"Totally" is informal filler. Consider removing it.',
    absolutely: '"Absolutely" is often unnecessary emphasis.',
    extremely: 'Consider a stronger single word instead of "extremely + adjective".'
  };

  const VOWEL_SOUND_EXCEPTIONS_AN = /^(hour|honest|honor|heir|herb)/i; // take "an"
  const CONSONANT_SOUND_EXCEPTIONS_A = /^(university|unique|unit|user|useful|one|once|european|euro|uniform)/i; // take "a"

  const SENTENCE_SPLIT = /[^.!?…]+[.!?…]*/g;
  const WORD_RE = /[A-Za-z']+/g;

  function isWordChar(ch) {
    return /[A-Za-z']/.test(ch || '');
  }

  function matchCase(source, replacement) {
    if (source.toUpperCase() === source && source.length > 1) {
      return replacement.toUpperCase();
    }
    if (source[0] === source[0].toUpperCase()) {
      return replacement[0].toUpperCase() + replacement.slice(1);
    }
    return replacement;
  }

  function issue(start, end, category, rule, message, suggestions) {
    return { start, end, category, rule, message, suggestions: suggestions || [] };
  }

  // ---- Rules ----------------------------------------------------------

  function checkSpelling(text, issues) {
    let m;
    const re = new RegExp(WORD_RE.source, 'g');
    while ((m = re.exec(text)) !== null) {
      const word = m[0];
      const correction = MISSPELLINGS[word.toLowerCase()];
      if (correction) {
        issues.push(issue(
          m.index, m.index + word.length,
          'correctness', 'spelling',
          `"${word}" appears to be misspelled.`,
          [matchCase(word, correction)]
        ));
      }
    }
  }

  function checkPhrases(text, issues) {
    for (const { find, fix } of PHRASE_FIXES) {
      const re = new RegExp('\\b' + find.replace(/'/g, "'") + '\\b', 'gi');
      let m;
      while ((m = re.exec(text)) !== null) {
        issues.push(issue(
          m.index, m.index + m[0].length,
          'correctness', 'grammar',
          `"${m[0]}" is grammatically incorrect.`,
          [matchCase(m[0], fix)]
        ));
      }
    }
  }

  function checkRepeatedWords(text, issues) {
    const re = /\b([A-Za-z]+)(\s+)\1\b/gi;
    let m;
    while ((m = re.exec(text)) !== null) {
      issues.push(issue(
        m.index, m.index + m[0].length,
        'correctness', 'repeated-word',
        `The word "${m[1]}" is repeated.`,
        [m[1]]
      ));
    }
  }

  function checkArticles(text, issues) {
    const re = /\b(a|an)\s+([A-Za-z]+)/gi;
    let m;
    while ((m = re.exec(text)) !== null) {
      const article = m[1];
      const word = m[2];
      const startsWithVowel = /^[aeiou]/i.test(word);
      let wantsAn = startsWithVowel;
      if (VOWEL_SOUND_EXCEPTIONS_AN.test(word)) wantsAn = true;
      if (CONSONANT_SOUND_EXCEPTIONS_A.test(word)) wantsAn = false;

      const hasAn = article.toLowerCase() === 'an';
      if (wantsAn !== hasAn) {
        const fixed = matchCase(article, wantsAn ? 'an' : 'a');
        issues.push(issue(
          m.index, m.index + article.length,
          'correctness', 'article',
          `Use "${fixed}" before "${word}".`,
          [fixed]
        ));
      }
    }
  }

  function checkSpacing(text, issues) {
    // Multiple spaces (not at line start, ignore leading indentation)
    let m;
    const multi = /[^\S\n]{2,}/g;
    while ((m = multi.exec(text)) !== null) {
      const before = text[m.index - 1];
      if (before === undefined || before === '\n') continue; // indentation
      issues.push(issue(
        m.index, m.index + m[0].length,
        'correctness', 'spacing',
        'Extra space found.',
        [' ']
      ));
    }
    // Missing space after punctuation: "word,word" / "end.Next"
    const noSpace = /([A-Za-z])([,.!?;:])([A-Za-z])/g;
    while ((m = noSpace.exec(text)) !== null) {
      // skip decimals-ish and common abbreviations like "e.g" / URLs
      const around = text.slice(Math.max(0, m.index - 4), m.index + 6).toLowerCase();
      if (/e\.g|i\.e|etc\.|www\.|\.com|\.org|\.net|\.io/.test(around)) continue;
      issues.push(issue(
        m.index + 1, m.index + 2,
        'correctness', 'spacing',
        `Missing space after "${m[2]}".`,
        [m[2] + ' ']
      ));
    }
    // Space before punctuation: "word ,"
    const spaceBefore = /([A-Za-z]) +([,.!?;:])/g;
    while ((m = spaceBefore.exec(text)) !== null) {
      issues.push(issue(
        m.index + 1, m.index + m[0].length,
        'correctness', 'spacing',
        `Unnecessary space before "${m[2]}".`,
        [m[2]]
      ));
    }
  }

  function checkCapitalization(text, issues) {
    // Standalone lowercase "i"
    let m;
    const loneI = /\bi\b(?!\.e|')/g;
    while ((m = loneI.exec(text)) !== null) {
      issues.push(issue(
        m.index, m.index + 1,
        'correctness', 'capitalization',
        'The pronoun "I" should be capitalized.',
        ['I']
      ));
    }
    // Sentence starts
    const sentStart = /(^|[.!?]\s+)([a-z])/gm;
    while ((m = sentStart.exec(text)) !== null) {
      const pos = m.index + m[1].length;
      // Skip if it's the lone "i" already flagged
      issues.push(issue(
        pos, pos + 1,
        'correctness', 'capitalization',
        'Sentences should start with a capital letter.',
        [text[pos].toUpperCase()]
      ));
    }
  }

  function checkFillers(text, issues) {
    for (const w of FILLERS) {
      const re = new RegExp('\\b' + w + '\\b', 'gi');
      let m;
      while ((m = re.exec(text)) !== null) {
        issues.push(issue(
          m.index, m.index + m[0].length,
          'clarity', 'filler',
          FILLER_ALTERNATIVES[w] || `"${m[0]}" may be unnecessary.`,
          ['']
        ));
      }
    }
  }

  function checkPassiveVoice(text, issues) {
    const re = /\b(is|are|was|were|been|being|be)\s+(\w+ed)\b/gi;
    let m;
    while ((m = re.exec(text)) !== null) {
      // skip common false positives (adjectives that end in -ed)
      if (/^(tired|excited|interested|worried|pleased|surprised|used|supposed)$/i.test(m[2])) continue;
      issues.push(issue(
        m.index, m.index + m[0].length,
        'engagement', 'passive-voice',
        `"${m[0]}" may be passive voice. Active voice is usually more engaging.`,
        []
      ));
    }
  }

  function checkLongSentences(text, issues) {
    let m;
    const re = new RegExp(SENTENCE_SPLIT.source, 'g');
    while ((m = re.exec(text)) !== null) {
      const words = m[0].match(WORD_RE);
      if (words && words.length > 30) {
        const start = m.index + (m[0].length - m[0].trimStart().length);
        issues.push(issue(
          start, m.index + m[0].length,
          'clarity', 'long-sentence',
          `This sentence has ${words.length} words. Consider splitting it for readability.`,
          []
        ));
      }
    }
  }

  // ---- Stats ----------------------------------------------------------

  function countSyllables(word) {
    word = word.toLowerCase().replace(/[^a-z]/g, '');
    if (!word) return 0;
    if (word.length <= 3) return 1;
    word = word.replace(/(?:[^laeiouy]es|ed|[^laeiouy]e)$/, '');
    const groups = word.match(/[aeiouy]{1,2}/g);
    return groups ? groups.length : 1;
  }

  function computeStats(text, issues) {
    const words = text.match(WORD_RE) || [];
    const sentences = (text.match(SENTENCE_SPLIT) || []).filter(s => s.trim());
    const wordCount = words.length;
    const sentenceCount = Math.max(sentences.length, wordCount ? 1 : 0);
    const syllables = words.reduce((n, w) => n + countSyllables(w), 0);

    let flesch = 0;
    if (wordCount > 0) {
      flesch = 206.835 - 1.015 * (wordCount / sentenceCount) - 84.6 * (syllables / wordCount);
      flesch = Math.max(0, Math.min(100, Math.round(flesch)));
    }

    // Overall score: start at 100, subtract weighted penalties, scaled by length
    const weights = { correctness: 3, clarity: 1.5, engagement: 1, delivery: 1 };
    const penalty = issues.reduce((n, i) => n + (weights[i.category] || 1), 0);
    const scale = Math.max(wordCount / 25, 1);
    const score = wordCount === 0 ? 100 : Math.max(0, Math.round(100 - (penalty / scale) * 4));

    return {
      words: wordCount,
      characters: text.length,
      sentences: wordCount ? sentences.length : 0,
      readingTimeSec: Math.ceil((wordCount / 225) * 60),
      readability: flesch,
      score,
      tone: detectTone(text)
    };
  }

  function detectTone(text) {
    if (!text.trim()) return 'Neutral';
    const lower = text.toLowerCase();
    const exclaims = (text.match(/!/g) || []).length;
    const contractions = (text.match(/\b\w+'(t|s|re|ll|ve|d|m)\b/gi) || []).length;
    const formalWords = (lower.match(/\b(therefore|furthermore|moreover|consequently|regarding|pursuant|hereby|accordingly)\b/g) || []).length;
    const friendlyWords = (lower.match(/\b(thanks|thank you|please|great|awesome|love|happy|glad)\b/g) || []).length;
    const confidentWords = (lower.match(/\b(will|definitely|certainly|guarantee|must|always|never)\b/g) || []).length;

    if (formalWords >= 2 && contractions === 0) return 'Formal';
    if (exclaims >= 2 || friendlyWords >= 2) return 'Friendly';
    if (confidentWords >= 3) return 'Confident';
    if (contractions >= 3) return 'Casual';
    return 'Neutral';
  }

  // ---- Entry point ----------------------------------------------------

  function checkText(text) {
    const issues = [];
    checkSpelling(text, issues);
    checkPhrases(text, issues);
    checkRepeatedWords(text, issues);
    checkArticles(text, issues);
    checkSpacing(text, issues);
    checkCapitalization(text, issues);
    checkFillers(text, issues);
    checkPassiveVoice(text, issues);
    checkLongSentences(text, issues);

    // Sort by position; drop exact-range duplicates (keep the first = higher priority)
    issues.sort((a, b) => a.start - b.start || a.end - b.end);
    const seen = new Set();
    const deduped = issues.filter(i => {
      const key = i.start + ':' + i.end + ':' + i.rule;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });

    return { issues: deduped, stats: computeStats(text, deduped) };
  }

  return { checkText, matchCase, countSyllables, detectTone };
});
