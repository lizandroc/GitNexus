# PROJECT.md — GitNexus Codebase Overview

> Written as a one-time deep knowledge transfer. Audience: an engineer or AI agent who has
> never seen this project. Companion files: **GAPS.md** (honest audit of weaknesses) and
> **CLAUDE.md** (operational instructions for AI coding sessions).

---

## 1. What this is

**GitNexus indexes a codebase into a knowledge graph and serves that graph to AI coding
agents.** It parses source files with Tree-sitter, resolves imports/calls/inheritance across
files, clusters related symbols into functional communities, traces execution flows
("processes") from entry points, and stores everything in an embedded graph database
(LadybugDB, formerly KuzuDB). AI agents (Claude Code, Cursor, Codex, Windsurf, OpenCode)
query the graph through an MCP server, so they can answer "what breaks if I change X?"
instead of grepping blindly.

**Who it's for:** developers who use AI coding agents and want those agents to understand
codebase structure — call chains, blast radius, cross-file dependencies — rather than
hallucinating them. The core value proposition is *precomputed relational intelligence*:
structure is computed at index time so tools return complete answers in one call, which
makes even small LLMs effective.

It is an open-source npm package (`gitnexus`, PolyForm Noncommercial license) with a
commercial enterprise offering by Akon Labs layered on top (not in this repo).

## 2. Monorepo layout

| Path | What it is | Published? |
|------|-----------|------------|
| `gitnexus/` | **The main product.** TypeScript CLI + ingestion pipeline + MCP server + local HTTP server. | npm package `gitnexus` |
| `gitnexus-web/` | React/Vite browser UI: graph visualization (Sigma.js) + LLM chat (LangChain). Today it is primarily a **client for `gitnexus serve`** (see §7 Surprises). | Deployed to Vercel (gitnexus.vercel.app) |
| `gitnexus-shared/` | Tiny shared package: graph type definitions, schema constants, language detection. Consumed via `file:` dependency and **inlined into `gitnexus/dist/_shared` at build time**. | No (bundled) |
| `eval/` | Python SWE-bench evaluation harness (baseline vs GitNexus-enhanced agents, via Docker + litellm/OpenRouter). | No |
| `gitnexus-claude-plugin/`, `gitnexus-cursor-integration/`, `.claude-plugin/` | Static skill/hook config for editor marketplaces. No build step. | Marketplace metadata |
| `.claude/skills/gitnexus/` | GitNexus's own agent skills, installed into this repo by `gitnexus analyze` (dogfooding). | — |
| `.github/` | CI (typecheck, tests, E2E), npm publish + release-candidate pipelines, LLM-powered issue triage sweep. | — |
| `docs/` | Deep-dive docs (COBOL indexing, plans/specs from past PRs). | — |

Root-level markdown worth knowing: `ARCHITECTURE.md` (pipeline DAG, where to change what),
`AGENTS.md`/`CLAUDE.md` (agent instructions; partially **generated** — see §7),
`GUARDRAILS.md`, `RUNBOOK.md`, `TESTING.md`, `CONTRIBUTING.md` (release process),
`type-resolution-system.md` / `type-resolution-roadmap.md` / `swift-ingestion-gaps.md`
(design notes that live at root rather than `docs/`).

## 3. Tech stack and why

| Piece | Choice | Evident reasoning |
|-------|--------|-------------------|
| Language | TypeScript (ESM, `"type": "module"`, Node ≥ 20) | Single language across CLI and web; strict tsc is the primary static gate. |
| Parsing | **Tree-sitter** native bindings, one grammar dependency per language (14+ languages) | Uniform AST interface across languages; incremental, error-tolerant parsing. Native bindings need `python3/make/g++` at install; `tree-sitter-kotlin`/`-swift`/`-dart`/`-proto` are *optional* deps so install never hard-fails. |
| Graph DB | **LadybugDB** (`@ladybugdb/core`) — embedded property-graph DB with Cypher, FTS and vector extensions | Zero-infrastructure local persistence in `.gitnexus/lbug`; Cypher is exposed directly to agents as a tool. Migrated from KuzuDB (renamed/abandoned upstream) — migration scars are still visible (`cleanupOldKuzuFiles`, `hasKuzuIndex`). |
| Graph algorithms | **Graphology** + a vendored Leiden implementation | Community detection (clusters) and in-memory graph manipulation before DB load. |
| Search | BM25 (LadybugDB FTS) + optional semantic vectors (transformers.js, default model `Snowflake/snowflake-arctic-embed-xs`, 384 dims) merged with **Reciprocal Rank Fusion** | Standard hybrid-search design; RRF avoids score normalization. Embeddings are **opt-in** (`--embeddings`) because generation is slow. |
| Agent interface | **MCP** over stdio (`@modelcontextprotocol/sdk`), plus MCP-over-HTTP in serve mode | The whole point of the product. Tool responses embed "**Next:** …" hints to guide weaker agents to the next call. |
| CLI | Commander with **lazy-loaded** subcommand modules (`cli/lazy-action.ts`) | MCP server startup time matters (editors spawn it); heavy imports (onnxruntime, tree-sitter) are deferred. |
| HTTP bridge | Express + CORS allowlist (localhost, RFC-1918 LAN, gitnexus.vercel.app) | Lets the hosted web UI talk to a local `gitnexus serve` without uploading code. |
| Web UI | React 18, Vite, Tailwind v4, Sigma.js/Graphology (WebGL graph), LangChain + LangGraph ReAct agent (user-supplied API keys) | Visual exploration + chat; provider keys stay in the browser (sessionStorage). |
| Tests | Vitest (forks pool) in both packages; Playwright for web E2E | See §6 — the vitest config encodes hard-won native-addon workarounds. |
| Lint/format | ESLint 9 flat config + Prettier at the **monorepo root**, husky + lint-staged pre-commit | Note: sub-package `npm test` etc. run from inside `gitnexus/`/`gitnexus-web/`, but lint/format run from the root. |

## 4. Architecture

```
                        gitnexus analyze [path]
                                 │
                                 ▼
         ┌────────────────────────────────────────────────┐
         │  Ingestion pipeline (DAG of phases)            │
         │  src/core/ingestion/pipeline.ts + runner.ts    │
         │                                                │
         │  scan → structure → [markdown, cobol] → parse  │
         │    → [routes, tools, orm] → crossFile → mro    │
         │    → communities → processes                   │
         └────────────────────┬───────────────────────────┘
                              │  in-memory KnowledgeGraph
                              ▼
         ┌────────────────────────────────────────────────┐
         │  LadybugDB load (CSV bulk COPY, then FTS +     │
         │  optional embeddings)                          │
         │  src/core/lbug/lbug-adapter.ts, csv-generator  │
         └────────────────────┬───────────────────────────┘
                              │
              .gitnexus/{lbug, meta.json}  (per-repo, gitignored)
              ~/.gitnexus/registry.json    (global repo registry)
                              │
      ┌───────────────────────┼────────────────────────────┐
      ▼                       ▼                            ▼
 gitnexus mcp            gitnexus serve              gitnexus query/impact/…
 (stdio MCP for          (Express on :4747,          (direct CLI tools for
  editors)                REST + MCP-over-HTTP        scripts/CI/eval)
      │                    for the web UI)                 │
      └───────────┬────────────┴───────────────────────────┘
                  ▼
        LocalBackend (src/mcp/local/local-backend.ts)
        — the single query engine behind every surface —
        reads registry, opens LadybugDB connections via a
        pooled adapter (max 5 repos, 8 conns each, 5-min idle
        eviction), implements query/context/impact/rename/
        detect_changes/cypher/group_* on top of Cypher.
```

**Key data contracts:**

- **Node tables:** File, Folder, Function, Class, Interface, Method, Property, Struct, Enum,
  Trait, Impl, …, plus Community, Process, Route, Tool, Section (markdown), CodeEmbedding.
- **One relationship table:** `CodeRelation` with a `type` property (CALLS, IMPORTS,
  EXTENDS, IMPLEMENTS, CONTAINS, DEFINES, HAS_METHOD, MEMBER_OF, STEP_IN_PROCESS,
  HANDLES_ROUTE, …) plus `confidence` (0–1 double) and `reason`. Every resolution decision
  carries a confidence score; impact analysis filters and reports on it.
- **Node IDs encode identity:** e.g. `Method:src/a.ts:Class.method#2~int$const` — arity
  suffix `#n`, same-arity type-hash suffix `~types`, C++ const suffix `$const`. IDs are
  *collision-only* tagged, so adding an overload changes existing IDs (documented in
  ARCHITECTURE.md "Known limitations").
- **meta.json:** `{repoPath, lastCommit, indexedAt, stats{files,nodes,edges,communities,processes,embeddings}}`.
  Staleness = `lastCommit != git HEAD` (checked in `src/core/git-staleness.ts`, surfaced by
  MCP tools as warnings).

**The multi-repo model:** one global MCP server serves every indexed repo. `analyze`
registers repos in `~/.gitnexus/registry.json`; tools take an optional `repo` parameter
that is only required when more than one repo is registered.

**Language support architecture (the heart of the codebase):** each language implements the
`LanguageProvider` interface (`src/core/ingestion/language-provider.ts`) in a single file
under `src/core/ingestion/languages/`. The provider table in `languages/index.ts` uses
`satisfies Record<SupportedLanguages, LanguageProvider>` so adding an enum entry without a
provider is a **compile error**. Per-language behavior is decomposed into parallel config
directories: `import-resolvers/`, `type-extractors/`, `method-extractors/configs/`,
`field-extractors/configs/`, `named-bindings/`, `call-sites/`, `route-extractors/`. The #1
historical source of bugs is *asymmetry* — a fix applied to one language's extractor but
not the other 13 (see GAPS.md).

**Cross-repo groups** (`src/core/group/`): a newer subsystem that extracts service
contracts (HTTP routes, gRPC, message topics, manifests) from multiple indexed repos,
matches producers to consumers, and stores links in a "bridge" database under
`~/.gitnexus/groups/` — enabling cross-repository impact analysis (`gitnexus group …`
commands and `group_*` MCP tools).

**Parsing concurrency:** `parse` phase uses a worker-thread pool
(`src/core/ingestion/workers/`) with a sequential fallback; a chunked AST cache and an
adaptive Tree-sitter buffer size (512KB–32MB) protect against memory exhaustion on large
repos.

## 5. Key design decisions (inferred, with reasoning)

1. **Precompute at index time, not query time.** Clustering, process tracing, entry-point
   scoring and confidence all happen during `analyze`. Tools then answer in one round-trip.
   This is the product thesis (documented in README) and explains why the pipeline is large
   and the query layer is mostly Cypher templating.
2. **DAG-of-phases pipeline** (refactored in PR #809). Each phase is a file with `name`,
   `deps`, typed output; the runner topo-sorts and validates. Add phases by appending to
   `buildPhaseList()` in `pipeline.ts`. This replaced an implicit ordering and is the
   sanctioned extension point.
3. **Confidence scores instead of binary edges.** Static resolution across 14 dynamic-ish
   languages cannot be exact, so edges carry confidence (e.g. exact param-type match = 1.0,
   variadic-vs-fixed = 0.7) and tools expose `minConfidence` filters. Never emit an edge
   without deciding its confidence.
4. **Two DB access paths on purpose:** `src/core/lbug/lbug-adapter.ts` is a
   single-connection singleton used by *analyze* (bulk writes, CSV COPY); pooled access
   (`pool-adapter.ts`, used by `LocalBackend`/serve/MCP) exists because LadybugDB
   connections are **not thread-safe** — concurrent queries on one connection segfault.
   The pool (one Database, many Connections, LRU-evicted) is the officially supported
   concurrency pattern.
5. **stdout hygiene for MCP.** MCP runs on stdio, so *anything* printed to stdout corrupts
   the protocol. The pool adapter saves `realStdoutWrite`/`realStderrWrite` and silences
   native-module output during connection warmup. Never `console.log` in code reachable
   from the MCP server path.
6. **Lazy everything at CLI startup.** Subcommands dynamically import their modules;
   onnxruntime is only imported when embeddings actually run (it crashes on mismatched Node
   ABI — issue #89). The 8GB heap re-spawn happens only in `analyze`.
7. **Generated agent-context files with sentinel markers.** `analyze` upserts a
   `gitnexus:start`/`gitnexus:end`-delimited block into the *indexed repo's* AGENTS.md and
   CLAUDE.md (`src/cli/ai-context.ts`) and installs skills into `.claude/skills/gitnexus/`.
   This repo indexes itself, so its own AGENTS.md/CLAUDE.md contain such generated blocks.
8. **Read-only Cypher enforcement by keyword blocklist.** `isWriteQuery()`
   (`pool-adapter.ts`) regex-blocks CREATE/DELETE/SET/MERGE/… for agent-facing Cypher.
9. **Best-effort non-fatal auxiliary steps.** FTS creation, AI-context generation,
   `.gitignore` updates, embedding restore are wrapped in swallow-all try/catch — an index
   is still produced if the extras fail. The flip side: failures are silent (see GAPS.md).
10. **Traceable releases.** Stable publishes on `v*` tags; every merge to `main` publishes
    an `-rc.N` to the `rc` dist-tag with idempotency marker tags (`rc/<sha>`), documented in
    CONTRIBUTING.md.

## 6. Critical paths — what is load-bearing

**Touch with maximum care (high blast radius, subtle invariants):**

- `src/core/ingestion/call-processor.ts` (~3,100 lines) — call extraction + receiver/type
  resolution for all languages. Most bug fixes in git history land here or in extractors.
- `src/core/ingestion/pipeline-phases/parse-impl.ts`, `cross-file-impl.ts`, and
  `src/core/ingestion/model/` (symbol table, type registry, resolution context) — the
  cross-file resolution engine; ordering (topological, consumer-before-provider cases) is
  tested by dozens of fixtures.
- `src/core/lbug/schema.ts` + `gitnexus-shared/src/lbug/schema-constants.ts` — node/edge
  schema. Any change invalidates existing indexes and must be reflected in `csv-generator.ts`,
  `lbug-adapter.ts`, MCP tool descriptions (`src/mcp/tools.ts` embeds the schema in prose),
  and resources.
- `src/mcp/local/local-backend.ts` (~3,200 lines) — every user-visible answer flows through
  it (MCP, HTTP, CLI tools). Node-ID parsing, staleness checks, repo resolution all live here.
- `src/core/lbug/pool-adapter.ts` — concurrency safety. Getting checkout/checkin wrong
  segfaults the MCP server.
- ID-generation logic (arity/type-hash/const suffixes) — impacts every downstream lookup.

**Moderately sensitive:** `src/server/api.ts` (CORS/security posture, streaming
back-pressure), `run-analyze.ts` (orchestration + embedding cache), `repo-manager.ts`
(registry format), `.github/workflows/release-candidate.yml` and `publish.yml`.

**Safe to change casually:** individual CLI command UX (`src/cli/list.ts`, `status.ts`…),
wiki generation (`src/core/wiki/` — excluded from coverage, LLM-dependent), web UI
components (`gitnexus-web/src/components/`), skills markdown (`gitnexus/skills/*.md`),
docs. Adding a *new* language provider or pipeline phase is designed to be additive and
low-risk if you follow the existing pattern files.

## 7. Surprises and traps for newcomers

1. **CLAUDE.md and AGENTS.md are partially machine-generated.** `gitnexus analyze`
   rewrites the region between the `gitnexus:start`/`gitnexus:end` HTML-comment markers.
   Hand edits inside the markers are lost on the next analyze (use `--skip-agents-md` to
   prevent). If the literal marker text appears anywhere else in the file (even inside
   backticks), the upsert logic (`ai-context.ts:upsertGitNexusSection`) will splice at the
   *first* occurrence — this has already corrupted CLAUDE.md once (duplicate stale block;
   see GAPS.md #7).
2. **The README oversells the current web UI.** It describes fully in-browser WASM
   indexing (Tree-sitter WASM, LadybugDB WASM, drag-and-drop ZIP). The current
   `gitnexus-web/src` contains **no indexing pipeline or WASM database** — it onboards by
   connecting to a local `gitnexus serve` backend (or asking the server to clone+analyze a
   URL). Don't go looking for browser indexing code; don't "fix" the web UI to match the README.
3. **Two lbug adapters, three embedder entry points.** `core/lbug/lbug-adapter.ts`
   (singleton, analyze-time writes) vs `core/lbug/pool-adapter.ts` (pooled reads) vs
   `mcp/core/lbug-adapter.ts` (MCP-facing re-export layer). Similarly
   `core/embeddings/embedder.ts` vs `mcp/core/embedder.ts`. Pick the one your call-site
   already uses; don't cross the streams (a write on a pooled connection while analyze owns
   the singleton = lock errors).
4. **LadybugDB native quirks dominate the test config.** `vitest.config.ts` runs
   lbug-touching integration tests in a dedicated sequential project
   (`fileParallelism: false`) and sets `dangerouslyIgnoreUnhandledErrors: true` because
   N-API destructors crash forks *at exit* on some platforms. Two integration tests
   (`lbug-core-adapter`, `search-core`) are known to fail in containers due to `/tmp` file
   locking. Don't "fix" these by reorganizing the config without understanding this.
5. **Analyze without `--embeddings` deletes existing embeddings.** The index is rebuilt
   from scratch each run (`fs.rm` of the lbug files); embeddings are only carried over via
   an explicit cache-and-restore step that runs when `--embeddings` is passed (and silently
   skipped entirely for repos > 50,000 nodes — `EMBEDDING_NODE_LIMIT` in `run-analyze.ts`).
6. **Ports:** `gitnexus serve` defaults to **4747** (AGENTS.md's mention of 3741 is stale);
   eval-server defaults to 4848; Vite dev server 5173.
7. **`gitnexus-shared` is not a real dependency at runtime.** It's a devDependency inlined
   by `gitnexus/scripts/build.js` into `dist/_shared` with import rewriting. Adding it to
   runtime `dependencies` breaks `npm install` for end users (already happened once — PR #803).
   Always build via `npm run build` (which is `node scripts/build.js`), not bare `tsc`.
8. **Stats in docs drift constantly.** Symbol/relationship counts in AGENTS.md/CLAUDE.md
   are snapshots from the last self-index; treat them as decorative. `--no-stats` exists to
   avoid the churn.
9. **The monorepo has no npm workspaces.** Each package has its own `package.json` and
   lockfile; you `cd` into `gitnexus/` or `gitnexus-web/` and run npm there. Root
   `package.json` only carries lint/format/husky.
10. **Windows is a first-class target.** Cross-platform CI (macOS, Windows), path handling
    (`path.sep`, backslash normalization), `GIT_ASKPASS` shims, and a note that Claude Code
    SessionStart hooks are broken on Windows (worked around via CLAUDE.md instead).
11. **Kuzu ghosts.** Older docs (`compound-engineering.local.md`, some comments) still
    reference `kuzu-adapter.ts` / `.gitnexus/kuzu` paths that no longer exist — the DB was
    renamed to LadybugDB and code moved to `lbug/`. Trust the code, not those docs.
