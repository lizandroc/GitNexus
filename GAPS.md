# GAPS.md — Honest Audit of Weaknesses

> Ordered by severity, most important first. Each entry: what it is, where it lives, why it
> matters, and a fix scoped small enough to execute as a single task. Severity scale:
> **CRITICAL / HIGH / MEDIUM / LOW**. See PROJECT.md for architecture context.

---

## 1. HIGH (security) — `gitnexus serve` HTTP API has no authentication at all

**What:** Every endpoint in `gitnexus/src/server/api.ts` — including `POST /api/analyze`
(accepts an arbitrary absolute local `path` or a remote git `url` to clone and index),
`GET /api/file` (reads any file inside an indexed repo), `GET /api/grep`, and
`POST /api/query` (raw Cypher) — is unauthenticated. CORS only restricts *browser* callers;
non-browser requests (no Origin header) are always allowed (`isAllowedOrigin`, api.ts:58),
and the CORS allowlist includes **all RFC-1918 LAN origins**. The server binds 127.0.0.1 by
default but `--host 0.0.0.0` is an advertised option (`src/cli/serve.ts`).

**Why it matters:** anyone who can reach the port (any LAN peer when `--host` is used, any
local process otherwise) can make the server index any readable directory on the machine and
then exfiltrate its file contents via `/api/file`/`/api/grep`, or trigger resource-heavy
clones/analyses. This is an arbitrary-file-read primitive gated only by network reachability.

**Fix (single task):** generate a random token at server startup (print it and/or write it to
`~/.gitnexus/serve-token`), require it via `Authorization: Bearer` middleware on all
`/api/*` routes except `/api/heartbeat`/`/api/info`, and have the web UI prompt for/store it.
At minimum, require the token whenever `--host` is not loopback. Add a unit test alongside
`gitnexus/test/unit/cors.test.ts`.

## 2. HIGH (security, needs verification) — read-only Cypher guard is a keyword blocklist

**What:** `isWriteQuery()` in `gitnexus/src/core/lbug/pool-adapter.ts:606` blocks
`CREATE|DELETE|SET|MERGE|REMOVE|DROP|ALTER|COPY|DETACH|FOREACH|INSTALL|LOAD` by regex. This
guards the agent-facing `cypher` MCP tool and `POST /api/query`. Blocklists are brittle:
LadybugDB/Kuzu-family databases also support statements like `EXPORT DATABASE '<path>'`,
`IMPORT DATABASE`, `ATTACH`, `USE`, `CALL <proc>` — none of which match the regex. If the
engine supports `EXPORT DATABASE`, an "untrusted" agent or LAN caller (see gap #1) can write
files to arbitrary paths.

**Why it matters:** the cypher tool is explicitly exposed to untrusted model output; a write
bypass corrupts indexes at best and writes to disk at worst.

**Fix (single task):** write a unit test in `gitnexus/test/unit/isWriteQuery.test.ts`
attempting `EXPORT DATABASE`, `IMPORT DATABASE`, `ATTACH`, `CALL`, and comment-obfuscated
variants against a scratch DB; then either extend the keyword list or (better) invert to an
allowlist: only queries starting with `MATCH`, `OPTIONAL MATCH`, `WITH`, `RETURN`, `UNWIND`,
`EXPLAIN` after stripping leading whitespace/comments.

## 3. HIGH (correctness/maintainability) — two ~3,000-line god modules on the hottest paths

**What:**
- `gitnexus/src/mcp/local/local-backend.ts` — 3,224 lines, ~40 responsibilities (repo
  registry, staleness, query, context, impact BFS, rename, detect_changes, group tools,
  route/tool maps, cluster/process queries, markdown formatting).
- `gitnexus/src/core/ingestion/call-processor.ts` — 3,141 lines of per-language call
  resolution.

**Why it matters:** every feature and every fix funnels through these files; merge conflicts,
accidental cross-feature breakage, and reviewer fatigue are structural. Most regressions in
git history (#793, #816, #817) live here.

**Fix (single task, repeatable):** extract one cohesive unit per task with its tests, no
behavior change. Good first slices: move `_runImpactBFS`/`_impactImpl`/`impactByUid` into
`src/mcp/local/impact.ts`; move `rename` into `src/mcp/local/rename.ts`; move the
`group*` handlers into `src/mcp/local/group-tools.ts`. Keep `LocalBackend` as a facade.

## 4. HIGH (test) — coverage floors are ~26% and the riskiest layers are excluded

**What:** `gitnexus/vitest.config.ts` sets coverage thresholds at statements 26 / branches 23
/ functions 28 / lines 27, and **excludes** `src/server/**` (the entire HTTP API — the
security surface from gap #1) and `src/core/wiki/**` from coverage. `gitnexus-web/src` has
**zero unit-test files colocated** (tests live in `gitnexus-web/test/unit`, small) and only
7 Playwright specs that require a manually running backend. The two known-flaky
lbug integration tests are documented to fail in containers, and
`dangerouslyIgnoreUnhandledErrors: true` swallows *all* unhandled errors in every test file,
not just the N-API exit crashes it was added for.

**Why it matters:** the ~3,850 existing tests are concentrated on language-resolution
fixtures; orchestration (`run-analyze.ts` error paths, server endpoints, pool eviction under
load) is where silent breakage will ship. `dangerouslyIgnoreUnhandledErrors` can mask real
async bugs in *any* test.

**Fix (single task each):** (a) add supertest-based endpoint tests for `/api/file` path
traversal, `/api/analyze` input validation, and auth once gap #1 lands, then delete
`src/server/**` from the coverage exclude list; (b) scope
`dangerouslyIgnoreUnhandledErrors` to the `lbug-db` vitest project only (it's currently in
the shared root config inherited by all projects).

## 5. MEDIUM (fragility) — string-interpolated Cypher fallback paths with manual escaping

**What:** `gitnexus/src/core/lbug/lbug-adapter.ts` (lines ~525–740) builds `CREATE`/`MERGE`
statements by string interpolation with hand-rolled `escapeValue`/`escapeLabel` (quote
doubling + backslash/newline replacement), used as the non-CSV fallback insert path. A
parameterized path exists (`executePrepared`, line ~805) but is not used everywhere.

**Why it matters:** symbol names and file contents come straight from arbitrary user
codebases. Any escaping gap (unicode escapes, `\r\n` variants, backtick in labels) corrupts
the index or enables Cypher injection *during indexing*. The old compound-engineering notes
already flagged this exact spot.

**Fix (single task):** convert the fallback node/relationship insert builders to
`executePrepared` with `$param` bindings, keeping only table/label names interpolated
through the existing `escapeTableName` allowlist. Add a unit test inserting a node whose
name is `'); DROP TABLE File;--` and content containing quotes/backslashes/newlines.

## 6. MEDIUM (reliability) — pervasive silent `catch {}` in the analyze orchestration

**What:** `gitnexus/src/core/run-analyze.ts` swallows failures of: embedding cache load, FTS
index creation ("best-effort"), cached-embedding re-insert, embedding count query, AI
context file generation, and lbug file deletion. `ai-context.ts` and `repo-manager.ts`
follow the same pattern.

**Why it matters:** users end up with an index that silently lacks search (FTS) or
embeddings, and the recorded symptom is "search returns nothing", far from the cause. The
GUARDRAILS "Signs" section exists precisely because these failures are invisible.

**Fix (single task):** thread the existing `onLog` callback into every swallowed catch with
a one-line warning (`FTS index creation failed: <msg> — keyword search will be degraded`),
and increment a `warnings` array on `AnalyzeResult` that `analyze.ts` prints at the end.
No behavior change otherwise.

## 7. MEDIUM (docs-as-code bug) — CLAUDE.md was corrupted by the generated-block upsert; README/AGENTS.md contain materially false claims

**What:**
- **CLAUDE.md** (before this knowledge-transfer commit) contained the generated gitnexus
  block **twice**: once spliced *into the middle of a sentence* under "## GitNexus rules"
  (with stats 4325/10556/300) and a second stale orphan copy (3298/7954/185). Root cause:
  `upsertGitNexusSection` (`gitnexus/src/cli/ai-context.ts:211`) splices at the first
  literal `gitnexus:start` marker occurrence — which was inside a backticked doc reference.
  AGENTS.md's changelog shows the same bug was fixed there manually (v1.2.0) but the code
  was never hardened.
- **README.md §Web UI** describes in-browser WASM indexing (drag-and-drop ZIP, Tree-sitter
  WASM, LadybugDB WASM, in-browser embeddings). `gitnexus-web/src` has none of that —
  it is a client for `gitnexus serve` (see PROJECT.md §7.2).
- **AGENTS.md** says "There is no ESLint/Prettier configuration in this repo" and "No
  separate lint command" (both false — root `eslint.config.mjs`, `npm run lint`, husky +
  lint-staged) and claims serve runs on port 3741 (it's 4747). **TESTING.md/CONTRIBUTING.md**
  say the pre-commit hook runs unit tests; `.husky/pre-commit` runs only lint-staged +
  typecheck ("Tests run in CI").

**Why it matters:** these files are loaded into every agent session; false instructions
make agents do the wrong thing (skip linting, look for WASM code, connect to the wrong port).

**Fix (single tasks):** (a) harden `upsertGitNexusSection` to require markers at line start
(regex `^<!-- gitnexus:start -->` with `m` flag) and to replace *all* stale blocks, with a
unit test reproducing the backticked-marker case; (b) rewrite README's Web UI section to
describe backend mode; (c) correct AGENTS.md lint/port/pre-commit claims. (CLAUDE.md itself
was repaired as part of this knowledge transfer.)

## 8. MEDIUM (duplication) — web UI keeps drifted copies of core modules instead of using `gitnexus-shared`

**What:** `gitnexus-web/src/core/graph/graph.ts` + `types.ts` duplicate
`gitnexus/src/core/graph/` (already drifted: the CLI copy has `removeNode`/relationship
removal; the web copy doesn't). `gitnexus-web/src/core/ingestion/cluster-enricher.ts`
duplicates `gitnexus/src/core/ingestion/cluster-enricher.ts`. `gitnexus-web/src/config/ignore-service.ts`
duplicates `gitnexus/src/config/ignore-service.ts`.

**Why it matters:** `gitnexus-shared` exists precisely to prevent this; fixes applied to one
copy won't reach the other (this is the same asymmetry failure mode the project already
suffers across languages).

**Fix (single task):** move `createKnowledgeGraph` and graph types into
`gitnexus-shared/src/graph/`, re-export from both packages, delete the web copies. Repeat as
separate tasks for cluster-enricher and ignore-service. Watch the `file:` + build-inline
mechanism (`gitnexus/scripts/build.js`) — run `npm run build` in `gitnexus/` to verify.

## 9. MEDIUM (half-finished) — KuzuDB→LadybugDB migration remnants and dead compatibility code

**What:** CHANGELOG "Unreleased" still carries the migration note (shipped long ago —
current version 1.6.1); `hasKuzuIndex()` in `repo-manager.ts` appears vestigial;
`compound-engineering.local.md` references non-existent `kuzu/schema.ts`, `kuzu-adapter.ts`
and a `detachKuzu()` pattern; `MIGRATION.md` is thin. Committed editor junk exists:
`.history/` (VS Code local-history snapshot), `.sisyphus/drafts/` (brainstorming notes),
empty `skills.mdm`, and a `.local.md` file that was presumably never meant to be committed.

**Why it matters:** dead references actively mislead agents (they will search for
kuzu-adapter.ts); junk files add noise to every repo-wide search.

**Fix (single task):** delete `.history/`, `.sisyphus/`, `skills.mdm`; add `.history/` and
`.sisyphus/` to `.gitignore`; move the still-useful parts of
`compound-engineering.local.md` into docs with corrected paths or delete it; fold the
CHANGELOG Unreleased block into the 1.6.x entries. Keep `cleanupOldKuzuFiles` (still
protects upgraders); decide on `hasKuzuIndex` by grepping call sites.

## 10. MEDIUM (edge cases) — known resolver blind spots are documented but scattered

**What:** Documented, deliberately-deferred gaps: Swift `if let`/`while let`/trailing
closures and multi-hop chains (`swift-ingestion-gaps.md`); TS `export *` / Rust re-export
DAG walk not implemented (`pipeline-phases/wildcard-synthesis.ts:260`, TODO(#821)); Swift
struct/enum/extension/actor extractor verification TODO
(`method-extractors/configs/swift.ts:269`); overload node-ID instability when a second
overload is added (ARCHITECTURE.md "ID stability"); no incremental indexing (full rebuild
every analyze — roadmap item).

**Why it matters:** these all silently degrade graph completeness — the product's core
promise. An agent told "impact analysis found no callers" may just be seeing a resolver gap.

**Fix (single task):** create GitHub issues (or a single tracking issue) from
`swift-ingestion-gaps.md` + the two TODOs so they're visible outside stray files, and add a
"Known blind spots" subsection to ARCHITECTURE.md linking them. Individual resolver fixes
are each their own well-scoped task with an existing fixture pattern to copy
(`test/fixtures/lang-resolution/<lang>-*`).

## 11. LOW (consistency) — naming and packaging inconsistencies

**What:**
- `gitnexus-web/package.json` is named `gitnexus` (same as the published CLI package),
  version 0.0.0 — confusing in tooling output.
- Design docs live at repo root (`type-resolution-system.md`, `type-resolution-roadmap.md`,
  `swift-ingestion-gaps.md`) while similar material lives under `docs/`.
- `vitest.config.ts` default project excludes `lbug-lock-retry.test.ts` twice (copy-paste).
- `run-analyze.ts` types `pipelineResult` as `any` in `AnalyzeResult`; several `any`s in
  `local-backend.ts` public signatures despite `@typescript-eslint/no-explicit-any: warn`.
- Web settings migrated API keys from localStorage to sessionStorage
  (`settings-service.ts`), but README still says "API keys stored in localStorage only".

**Why it matters:** low individually; collectively they erode trust in what the repo says
about itself.

**Fix (single task):** rename web package to `gitnexus-web`; move the three root design docs
under `docs/design/` and fix inbound links; delete the duplicate exclude line; type
`pipelineResult` as `PipelineResult | undefined`; correct the README storage claim.

## 12. LOW (ops) — eval harness and CI odds-and-ends

**What:** `eval/` requires Docker + API keys and is never exercised in CI (fine, but no
smoke test of `tool_registry.py`/formatters means Python bit-rot is invisible — note
`eval/tests` exists but isn't wired into any workflow). `ci.yml` carries a
`TODO(post-merge)` back-compat block writing artifact files under two naming schemes for
`ci-report.yml`. The triage sweep workflow (`.github/scripts/triage/`) embeds a Python
embedding pipeline with its own requirements — unowned by any test job.

**Why it matters:** slow rot in tooling that only fails when someone finally needs it.

**Fix (single task):** add a `eval-smoke` job (ubuntu, `uv run pytest eval/tests -q`, no
Docker/keys) gated on `eval/**` path changes; remove the ci.yml back-compat block now that
the underscore reader is on main (verify first).

---

### Explicit notes on things that look like gaps but aren't

- **Two lbug adapters (singleton vs pool)** — intentional; LadybugDB connections are not
  thread-safe. Don't unify without understanding PROJECT.md §5.4.
- **`dangerouslyIgnoreUnhandledErrors`** — needed for N-API destructor exit crashes, but
  should be *scoped* (gap #4b), not removed.
- **`isAllowedOrigin` allowing requests without an Origin header** — correct for CORS
  (curl/server-to-server aren't browser-credential attacks); the real issue is missing
  auth (gap #1), not the CORS predicate.
- **Low-level `catch {}` around `closeLbug()` in error paths** — deliberate double-close
  protection, fine.
- **SSRF validation in `server/git-clone.ts`** — actually quite thorough (metadata
  hostnames, IPv4/IPv6 private ranges, decimal/hex encodings). One residual: hostnames that
  *resolve* to private IPs (DNS rebinding at git level) are not caught; acceptable for a
  localhost tool, worth revisiting if auth (#1) is ever bypassed.
