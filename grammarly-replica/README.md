# QuillCheck — a Grammarly-style writing assistant for macOS

QuillCheck is a native-feeling macOS desktop app (built with Electron) that checks
your writing as you type, Grammarly-style: inline underlines in the editor, a
suggestions sidebar with one-click fixes, an overall writing score, tone
detection, and readability stats.

Everything runs **100% locally** — no account, no network calls, your text never
leaves your Mac.

## Features

- **Live checking as you type** with colored underlines by category:
  - 🔴 **Correctness** — misspellings, grammar ("could of" → "could have"),
    repeated words, a/an agreement, capitalization, spacing/punctuation
  - 🔵 **Clarity** — filler words ("very", "just", "basically"…), overlong sentences
  - 🟢 **Engagement** — passive-voice detection
- **Suggestions sidebar** with Apply / Dismiss on every card, filterable by category
- **Writing score ring** (0–100) like Grammarly's performance score
- **Tone detector** (Formal / Friendly / Confident / Casual / Neutral)
- **Live stats**: words, characters, sentences, reading time, Flesch readability

## Run it on your Mac

Requires [Node.js](https://nodejs.org) 18+.

```bash
cd grammarly-replica
npm install
npm start
```

## Build a standalone Mac app (.dmg)

```bash
npm run dist
```

The `.dmg` and `.zip` land in `dist/`. Open the dmg and drag **QuillCheck** to
Applications. (For distribution outside your machine you'd add code-signing /
notarization config; for personal use this is enough — right-click → Open the
first time if Gatekeeper complains.)

## Run the engine tests

```bash
npm test
```

## Project layout

```
grammarly-replica/
├── main.js              # Electron main process (window + macOS menu)
├── preload.js           # Context-isolated bridge (minimal)
├── renderer/
│   ├── index.html       # App shell
│   ├── styles.css       # macOS-flavored UI styling
│   ├── engine.js        # Rule-based checking engine (no DOM deps, Node-testable)
│   └── app.js           # Editor + sidebar wiring
└── test/
    └── engine.test.js   # Engine unit tests (plain Node, no test framework)
```

## How the checking works

`renderer/engine.js` is a self-contained, dependency-free analyzer:

- a ~130-entry common-misspellings dictionary with case-preserving corrections
- phrase-level grammar rules (`could of`, `he don't`, `we was`, …)
- regex rules for repeated words, a/an agreement (with sound-based exceptions
  like "an hour" / "a university"), spacing, and capitalization
- style heuristics: filler words, passive voice, 30+ word sentences
- stats: Flesch Reading Ease, reading time, and a weighted overall score

Because it's plain JavaScript with no DOM or Electron dependencies, the same
file powers the app and the Node test suite.
