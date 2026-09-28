<!-- version: 2.0.0 -->
<!--
  Metadata: version, last reviewed, scope, model policy, reference docs, changelog.
  Last updated: 2026-09-28
-->

Last reviewed: 2026-09-28

**Project:** GitNexus · **Environment:** dev · **Maintainer:** repository maintainers (see GitHub)

Follow **AGENTS.md** for the canonical agent rules; this file adds Claude Code–specific and
operational instructions. Start here every session.

## Read these first

- **[PROJECT.md](PROJECT.md)** — architecture, data flow, design decisions, critical paths, and the traps for newcomers. Read before touching the ingestion pipeline, LocalBackend, or the DB layer.
- **[GAPS.md](GAPS.md)** — severity-ordered audit of known weaknesses, each with a scoped fix. Check it before "discovering" a problem or picking up cleanup work.
- **[AGENTS.md](AGENTS.md)** / **[GUARDRAILS.md](GUARDRAILS.md)** — canonical agent rules and non-negotiables. Note: AGENTS.md has known stale claims (lint config, port 3741) — see GAPS.md #7; this file is authoritative for commands.

## Scope

See the **Scope** table in [AGENTS.md](AGENTS.md) for read/write/execute/off-limits boundaries.

## Commands that matter

No npm workspaces — `cd` into the package first. Root holds only lint/format/husky.

```bash
# CLI / core (gitnexus/) — the main product
cd gitnexus
npm install                 # triggers prepare (full build) + postinstall (tree-sitter-swift patch)
npm run build               # node scripts/build.js — NEVER bare tsc (inlines gitnexus-shared into dist/_shared)
npm test                    # all vitest tests (unit + integration, ~3800)
npm run test:unit           # fast loop
npm run test:integration    # lbug-* tests run sequentially by design; 2 may fail in containers (known, /tmp locking)
npx tsc --noEmit            # typecheck (matches CI)
npm run dev                 # tsx watch src/cli/index.ts
node dist/cli/index.js analyze|mcp|serve|query|impact|...   # run a built command

# Web UI (gitnexus-web/) — build gitnexus-shared first
cd gitnexus-shared && npm install && npm run build
cd gitnexus-web && npm install
npm run dev                 # Vite on :5173
npm test                    # unit tests
npx tsc -b --noEmit         # typecheck (matches CI)
npm run test:e2e            # Playwright — requires `gitnexus serve` (:4747) AND `npm run dev` running

# Lint / format (repo ROOT, not per-package)
npm run lint / lint:fix / format / format:check
```

- **Deploy/release:** stable = push a `v*` tag (`.github/workflows/publish.yml`); every merge to `main` auto-publishes an `-rc.N` to the npm `rc` dist-tag (`release-candidate.yml`). Never publish manually. Details in CONTRIBUTING.md §Releases.
- **Pre-commit hook** (`.husky/pre-commit`): lint-staged (prettier+eslint) + `tsc` for changed packages. It does **not** run tests — run them yourself before pushing.
- **CI** = typecheck + vitest w/ coverage (ubuntu/macOS/Windows) + Playwright E2E (only when `gitnexus-web/` changes). Coverage floors auto-ratchet — don't lower thresholds in `gitnexus/vitest.config.ts`.

## Conventions this codebase actually follows

- **TypeScript ESM everywhere** (`"type": "module"`, Node ≥ 20). Relative imports use explicit `.js` extensions in `gitnexus/`.
- **Files:** kebab-case (`local-backend.ts`, `call-processor.ts`). Named exports; classes for stateful services (`LocalBackend`, `JobManager`), plain functions/consts elsewhere.
- **Per-language logic goes in per-language config files**, never inline `if (language === ...)` in shared processors. One file per language under `src/core/ingestion/languages/` (the `LanguageProvider` contract) plus mirrors in `import-resolvers/`, `type-extractors/`, `method-extractors/configs/`, `field-extractors/configs/`, `named-bindings/`. The provider table in `languages/index.ts` uses `satisfies` for compile-time exhaustiveness — a new language that misses a provider fails `tsc`.
- **Pipeline changes = new phase file** in `src/core/ingestion/pipeline-phases/` with `name`, `deps`, typed output, exported from `index.ts`, appended in `pipeline.ts:buildPhaseList()`. Follow the template in ARCHITECTURE.md.
- **Every graph edge carries `confidence` (0–1) and `reason`.** When adding resolution logic, decide the confidence tier explicitly (see ARCHITECTURE.md confidence table).
- **Error handling:** auxiliary steps (FTS, AI-context files, gitignore) are best-effort try/catch; pipeline/DB-load failures must throw. `run-analyze.ts` must never `process.exit()` — callers own process lifecycle.
- **Tests:** vitest, colocated under `gitnexus/test/{unit,integration}`; language-resolution behavior is tested via mini-repo fixtures in `test/fixtures/lang-resolution/<lang>-<case>/`. Copy an existing fixture dir when adding one.
- **Commits:** conventional commits (`feat:`, `fix:`, `docs:`; optional scope like `fix(extractors):`). PR titles `[area] Description`.
- **Web styling:** Tailwind v4 utility classes; prettier-plugin-tailwindcss orders them. State via React context (`useAppState`) — no Redux.

## Gotchas (things that look right but aren't)

- **`npm run build` in `gitnexus/` is a custom script**, not tsc: it builds `gitnexus-shared`, compiles, copies shared into `dist/_shared`, and rewrites imports. Bare `tsc` output is broken at runtime. Never add `gitnexus-shared` to runtime `dependencies` (broke end-user installs once, PR #803).
- **AGENTS.md and CLAUDE.md are partially generated.** `gitnexus analyze` rewrites the block between the `gitnexus:start` / `gitnexus:end` HTML-comment markers (code: `src/cli/ai-context.ts`). Never hand-edit inside the markers; never write the literal marker text anywhere else in these files (the upsert splices at the first occurrence — it corrupted this file once). Use `--skip-agents-md` to protect manual edits.
- **MCP runs on stdio → stdout is protocol.** No `console.log` in any code reachable from `mcp.ts`/`LocalBackend`/pool-adapter. Use the existing `realStdoutWrite`/stderr patterns.
- **LadybugDB connections are not thread-safe.** Writes during analyze use the singleton `core/lbug/lbug-adapter.ts`; concurrent reads (MCP/serve) use `core/lbug/pool-adapter.ts`. Don't mix them, don't share a Connection across concurrent queries (segfault), don't run analyze while an MCP server holds the same repo open (lock errors).
- **`analyze` rebuilds from scratch and DELETES embeddings unless `--embeddings` is passed.** Repos > 50k nodes silently skip embeddings (`EMBEDDING_NODE_LIMIT`).
- **Ports:** `serve` = 4747 (AGENTS.md's 3741 is wrong), eval-server = 4848, Vite = 5173.
- **The web UI has no in-browser indexing** despite README claims — it's a client for `gitnexus serve`. Don't hunt for WASM pipeline code in `gitnexus-web/`.
- **Vitest config is load-bearing:** lbug-touching integration tests run in a sequential project; `dangerouslyIgnoreUnhandledErrors` exists for N-API exit crashes. Two tests (`lbug-core-adapter`, `search-core`) fail in containers — environment issue, not your bug.
- **Optional tree-sitter deps** (kotlin/swift/dart/proto) warn on install — expected, non-blocking. Native builds need `python3`, `make`, `g++`.
- **Old "kuzu" references in stray docs are dead** — the DB layer is `src/core/lbug/` now.

## Rules

- **Never change without care:** node-ID generation (arity `#n` / type-hash `~t` / `$const` suffixes), `core/lbug/schema.ts` + `gitnexus-shared` schema constants (invalidates every existing index; must sync `csv-generator.ts`, tool descriptions in `mcp/tools.ts`, resources), `pool-adapter.ts` checkout/checkin, `isWriteQuery` (security guard), release workflows.
- **When fixing a language extractor, check all 14 languages for the same asymmetry** — it is the #1 historical bug source. Grep the parallel config dirs for the pattern you're fixing.
- **Generated/managed files:** the marker-delimited blocks in AGENTS.md/CLAUDE.md, `.claude/skills/gitnexus/**` (reinstalled by analyze), `.gitnexus/` (never commit), `~/.gitnexus/registry.json`. `gitnexus/vendor/` and `gitnexus-web/src/vendor/` are vendored — don't lint/refactor.
- Keep diffs minimal; no drive-by refactors; update lockfiles only when dependencies change; never commit secrets (GUARDRAILS.md is binding).
- Validation before pushing: `cd gitnexus && npx tsc --noEmit && npm test`, and for web `cd gitnexus-web && npx tsc -b --noEmit && npm test`.

## Claude Code specifics

- Prefer **PreToolUse** hooks for hard gates (e.g. typecheck before `git commit`); a PostToolUse hook re-indexes after commits when GitNexus hooks are installed.
- On long sessions, summarize progress in chat or a local scratch file (do **not** commit `HANDOFF.md`), then `/clear` and resume.

## Changelog

| Date | Version | Change |
|------|---------|--------|
| 2026-09-28 | 2.0.0 | Knowledge-transfer rewrite: commands/conventions/gotchas/rules; fixed duplicated generated block; added PROJECT.md + GAPS.md pointers. |
| 2026-04-13 | 1.3.0 | Updated GitNexus index stats after DAG refactor. |
| 2026-03-24 | 1.2.0 | Removed duplicated gitnexus:start block and scope table; replaced with pointers to AGENTS.md. |
| 2026-03-23 | 1.1.0 | Updated agent instructions to match AGENTS.md. |
| 2026-03-22 | 1.0.0 | Added structured header and changelog. |

---

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **GitNexus** (4325 symbols, 10556 relationships, 300 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## When Debugging

1. `gitnexus_query({query: "<error or symptom>"})` — find execution flows related to the issue
2. `gitnexus_context({name: "<suspect function>"})` — see all callers, callees, and process participation
3. `READ gitnexus://repo/GitNexus/process/{processName}` — trace the full execution flow step by step
4. For regressions: `gitnexus_detect_changes({scope: "compare", base_ref: "main"})` — see what your branch changed

## When Refactoring

- **Renaming**: MUST use `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` first. Review the preview — graph edits are safe, text_search edits need manual review. Then run with `dry_run: false`.
- **Extracting/Splitting**: MUST run `gitnexus_context({name: "target"})` to see all incoming/outgoing refs, then `gitnexus_impact({target: "target", direction: "upstream"})` to find all external callers before moving code.
- After any refactor: run `gitnexus_detect_changes({scope: "all"})` to verify only expected files changed.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Tools Quick Reference

| Tool | When to use | Command |
|------|-------------|---------|
| `query` | Find code by concept | `gitnexus_query({query: "auth validation"})` |
| `context` | 360-degree view of one symbol | `gitnexus_context({name: "validateUser"})` |
| `impact` | Blast radius before editing | `gitnexus_impact({target: "X", direction: "upstream"})` |
| `detect_changes` | Pre-commit scope check | `gitnexus_detect_changes({scope: "staged"})` |
| `rename` | Safe multi-file rename | `gitnexus_rename({symbol_name: "old", new_name: "new", dry_run: true})` |
| `cypher` | Custom graph queries | `gitnexus_cypher({query: "MATCH ..."})` |

## Impact Risk Levels

| Depth | Meaning | Action |
|-------|---------|--------|
| d=1 | WILL BREAK — direct callers/importers | MUST update these |
| d=2 | LIKELY AFFECTED — indirect deps | Should test |
| d=3 | MAY NEED TESTING — transitive | Test if critical path |

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/GitNexus/context` | Codebase overview, check index freshness |
| `gitnexus://repo/GitNexus/clusters` | All functional areas |
| `gitnexus://repo/GitNexus/processes` | All execution flows |
| `gitnexus://repo/GitNexus/process/{name}` | Step-by-step execution trace |

## Self-Check Before Finishing

Before completing any code modification task, verify:
1. `gitnexus_impact` was run for all modified symbols
2. No HIGH/CRITICAL risk warnings were ignored
3. `gitnexus_detect_changes()` confirms changes match expected scope
4. All d=1 (WILL BREAK) dependents were updated

## Keeping the Index Fresh

After committing code changes, the GitNexus index becomes stale. Re-run analyze to update it:

```bash
npx gitnexus analyze
```

If the index previously included embeddings, preserve them by adding `--embeddings`:

```bash
npx gitnexus analyze --embeddings
```

To check whether embeddings exist, inspect `.gitnexus/meta.json` — the `stats.embeddings` field shows the count (0 means no embeddings). **Running analyze without `--embeddings` will delete any previously generated embeddings.**

> Claude Code users: A PostToolUse hook handles this automatically after `git commit` and `git merge`.

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
