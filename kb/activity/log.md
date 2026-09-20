# Activity Log

## Operating rules
- Append-only.
- Record one entry per mutating batch.
- Name the `raw`, `wiki`, `indexes`, `schema`, and `config` surfaces touched in each batch.
- Call out `canonical material`, `provenance`, and `derived output` decisions explicitly.
- Record vault-impact details whenever frontmatter, aliases, embeds, or shared `.obsidian/` surfaces change.

## Entry template

### [YYYY-MM-DD HH:MM] [Batch label]
- Mode: [create|ingest|enrich|derive|improve|migration]
- Summary: [one sentence]
- `raw`: [files added or updated]
- `wiki`: [files added or updated]
- `indexes`: [files added or updated]
- `schema`: [files added or updated / unchanged]
- `config`: [files added or updated / unchanged]
- `canonical material`: [unchanged / annotated / approved exception]
- `provenance`: [what is now linked or what remains missing]
- `derived output`: [none / path / regeneration note]
- `vault`: [frontmatter, aliases, embeds, or shared `.obsidian/` surfaces changed / unchanged]
- `path map`: [old -> new note names or paths if migration work occurred / none]
- `link/backlink impact`: [what navigation changed and what stayed stable]
- Risks / rollback: [if relevant]
- Follow-up:
  - [ ]

## Initial entry example

### [2026-04-14 00:00] Bootstrap
- Mode: create
- Summary: Initialized the layered KB structure.
- `raw`: seeded directories only
- `wiki`: added `wiki/index.md`
- `indexes`: added `indexes/source-map.md` and `indexes/coverage.md`
- `schema`: unchanged
- `config`: added `config/obsidian-vault.md`
- `canonical material`: none yet
- `provenance`: placeholder sections only
- `derived output`: none
- `vault`: initialized `.obsidian/` shared surfaces and note metadata defaults
- `path map`: none
- `link/backlink impact`: root indexes now provide the first stable navigation surface
- Risks / rollback: remove only the new scaffold if the KB root was created in error
- Follow-up:
  - [ ] Add the first source to `raw/`

### [2026-04-14 00:01] Companion KB Seed
- Mode: create
- Summary: Replaced the bootstrap placeholders with repo-specific `wiki`, `indexes`, `schema`, `config`, and `raw` seed content for an Obsidian-first companion KB.
- `raw`: added initial internal and external extract manifests under `raw/extracts/`
- `wiki`: added route, model, operations, tooling, and source-summary notes
- `indexes`: added canonical-material, docs-surface, skill-surface, internal-source, external-source, ingest-queue, source-map, and coverage indexes
- `schema`: added initial page-type, field, and collection contracts
- `config`: refined `config/obsidian-vault.md` and added ingest/provenance contracts
- `canonical material`: unchanged; repo docs/code remain authoritative
- `provenance`: linked each maintained note back to repo paths or planned external raw captures
- `derived output`: none
- `vault`: retained shared `.obsidian/` starter templates and documented companion-KB behavior
- `path map`: none
- `link/backlink impact`: root `wiki` and `indexes` now provide stable navigation for future enrich work
- Risks / rollback: this is additive scaffold content only; rollback is limited to removing the new `kb/` tree
- Follow-up:
  - [ ] Ingest first-wave external source captures into `raw/sources/external/`
  - [ ] Add contributor and stakeholder route notes if the KB expands beyond the current maintainer focus

### [2026-04-14 00:02] External Raw Mirror Wave 1
- Mode: ingest
- Summary: Added the first broad external raw mirror across public contract, upstream NBA API, distribution, data stack, and tooling/vault collections.
- `raw`: added capture notes under `raw/sources/external/public-contract/`, `raw/sources/external/upstream-nba/`, `raw/sources/external/distribution/`, `raw/sources/external/data-stack/`, and `raw/sources/external/tooling-vault/`
- `wiki`: refreshed source-summary notes to point at the captured external collections
- `indexes`: refreshed `indexes/source-map.md`, `indexes/external-sources.md`, `indexes/ingest-queue.md`, and `raw/extracts/external/source-collections.md`
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged
- `provenance`: linked external collections into the source summaries and source map
- `derived output`: none
- `vault`: unchanged
- `path map`: none
- `link/backlink impact`: external-source indexes now point at concrete captured directories instead of planned-only collections
- Risks / rollback: some public sites required failure-aware stubs instead of clean markdown captures; replace those later rather than deleting the records
- Follow-up:
  - [ ] Ingest additional published examples and docs-app stack sources
  - [ ] Replace the Obsidian Properties and PyPI stubs with fuller captures if access improves

### [2026-04-14 00:03] External Raw Mirror Wave 2
- Mode: ingest
- Summary: Added published Kaggle example captures, docs-app stack captures, and deeper KB topic notes for project, extractor, docs generator, and chat/query surfaces.
- `raw`: added `raw/sources/external/published-examples/` and `raw/sources/external/docs-app-stack/`
- `wiki`: added `project-overview`, `docs-autogen`, `docs-app-stack`, `extractor-surface`, `query-agent`, `chat-surface`, and `published-examples-source-summary`
- `indexes`: refreshed `source-map`, `external-sources`, `ingest-queue`, and `coverage`
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged
- `provenance`: linked second-wave external collections into the new topic notes
- `derived output`: none
- `vault`: unchanged
- `path map`: none
- `link/backlink impact`: the KB now has explicit notes for docs generation, chat runtime, extractor surface, and published examples
- Risks / rollback: published Kaggle notebook captures remain stub-heavy because the notebook pages were fetch-limited
- Follow-up:
  - [ ] Capture richer notebook metadata if access improves
  - [ ] Add dedicated topic notes for model-audit, docs generator internals, and query cookbook families

### [2026-04-14 00:04] KB Enrichment Wave 3
- Mode: enrich
- Summary: Added high-value internal topic notes for docs generator internals, browser playground behavior, model audit, and query-cookbook routing, plus supporting internal extract manifests.
- `raw`: added `raw/extracts/internal/chat-surface-manifest.md` and `raw/extracts/internal/docs-app-stack-inventory.md`
- `wiki`: added `docs-generator-internals`, `playground-lane`, `model-audit`, and `query-cookbook-families`
- `indexes`: refreshed `source-map`, `coverage`, and root wiki navigation
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged
- `provenance`: linked new notes to internal manifests, repo code, and external docs-app stack captures
- `derived output`: none
- `vault`: unchanged
- `path map`: none
- `link/backlink impact`: topic-level navigation is now stronger for docs generation, playground behavior, and model-audit work
- Risks / rollback: additive note batch only; no existing canonical material moved or rewritten
- Follow-up:
  - [ ] Add component-level docs-app notes if the docs surface becomes an active maintenance lane
  - [ ] Add deeper query-cookbook family examples if the analytics KB grows into a cookbook reference

### [2026-04-14 00:05] KB Enrichment Wave 4
- Mode: ingest + enrich
- Summary: Added a much larger fourth wave covering deeper NBA API docs, warehouse docs, docs-framework docs, agent-runtime docs, six new topic notes, and two new internal manifests.
- `raw`: added `nba-api-deep`, `warehouse-deep`, `docs-framework-deep`, and `agent-runtime-deep` external collections plus `analytics-helper-surface-manifest` and `lineage-audit-inventory`
- `wiki`: added `metric-calculator-surface`, `season-time-semantics`, `visualization-surface`, `docs-component-registry`, `lineage-internals`, and `query-safety`
- `indexes`: refreshed `external-sources`, `ingest-queue`, `source-map`, `coverage`, and root wiki navigation
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged
- `provenance`: linked the new deep collections to the new topic notes and manifests
- `derived output`: none
- `vault`: unchanged
- `path map`: none
- `link/backlink impact`: the KB now has deeper coverage for safety, lineage internals, docs components, metric helpers, and season semantics
- Risks / rollback: some deep framework and agent-runtime URLs required stub captures because the public endpoint moved or returned a 404 shell
- Follow-up:
  - [ ] Add dedicated topic notes for specific visualization helpers or cookbook families if usage becomes heavy
  - [ ] Replace stub captures with fuller extracts when access paths improve

### [2026-04-14 00:06] KB Enrichment Wave 5
- Mode: ingest + enrich
- Summary: Added another extra-large wave with deep Kaggle, docs-runtime, visualization, and LangGraph captures plus eight new topic notes and two new internal manifests.
- `raw`: added `kaggle-deep`, `docs-runtime-deep`, `viz-deep`, and `langgraph-deep` external collections plus `helper-module-breakdown` and `docs-admin-search-inventory`
- `wiki`: added `court-helper-internals`, `comparison-similarity-helpers`, `lineup-trend-helpers`, `docs-admin-surface`, `kaggle-publishing-lane`, `docs-search-surface`, `chainlit-runtime`, and `export-share-artifacts`
- `indexes`: refreshed `external-sources`, `ingest-queue`, `source-map`, `coverage`, and root wiki navigation
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged
- `provenance`: linked the new deep collections to runtime, admin, export, helper, and publishing notes
- `derived output`: none
- `vault`: unchanged
- `path map`: none
- `link/backlink impact`: helper and runtime topics now have stronger raw-source coverage and discoverability
- Risks / rollback: a handful of deep pages still required stub captures because the upstream route moved or was unavailable
- Follow-up:
  - [ ] Add topic notes for admin telemetry internals or notebook publishing internals if the KB keeps expanding
  - [ ] Replace remaining stubs with fuller captures when source accessibility improves

### [2026-04-14 00:07] KB Enrichment Wave 6
- Mode: ingest + enrich
- Summary: Resumed the interrupted doubled wave and added deeper Chainlit, Copilot, docs-admin, DuckDB-WASM, advanced NBA API, and notebook-metadata captures plus route, topic, and manifest coverage for chrome, telemetry, prompts, MCP, sandbox, and skills.
- `raw`: added `chainlit-deep`, `copilot-deep`, `docs-admin-deep`, `duckdb-wasm-deep`, `nba-api-advanced`, and `kaggle-notebook-metadata` external collections plus six new internal manifests
- `wiki`: added contributor/stakeholder routes, topic family and stub-replacement indexes, and topic notes for docs chrome, telemetry, DuckDB-WASM runtime, search query expansion, artifact store, sandbox contract, prompt assembly, profile/settings, MCP surface, and chat skills
- `indexes`: refreshed `external-sources`, `ingest-queue`, `source-map`, and root wiki navigation
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged
- `provenance`: linked new raw collections and internal manifests into runtime, route, admin, and export topics
- `derived output`: none
- `vault`: unchanged
- `path map`: none
- `link/backlink impact`: the KB now has stronger route coverage, admin/docs runtime coverage, and deeper chat/runtime surface mapping
- Risks / rollback: several new deep captures are stub-heavy because upstream docs moved or were unavailable
- Follow-up:
  - [ ] Add dedicated notes for notebook publishing internals and admin telemetry internals if the KB continues expanding
  - [ ] Replace new stub captures as upstream access paths stabilize

### [2026-04-15 00:09] KB Enrichment Wave 7
- Mode: enrich
- Summary: Added the remaining high-value service-layer, notebook/bootstrap, tracing, catalog, memory, and finer-grained docs-admin notes, plus supporting service/admin inventories.
- `raw`: added `chat-service-layer-inventory` and `docs-admin-page-inventory`
- `wiki`: added service/runtime notes for semantic catalog, SQL validator, memory store, Copilot backend, web context tools, notebook/bootstrap, launcher, tracing, access mode, and finer-grained docs-admin pages
- `indexes`: refreshed `wiki/index.md`, `coverage`, `topic-family-map`, `source-map`, and `activity/log.md`
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged
- `provenance`: linked the new service-layer and admin-page inventories into the new note cluster
- `derived output`: none
- `vault`: unchanged
- `path map`: none
- `link/backlink impact`: the KB now has dedicated notes for the main remaining chat service and docs-admin page surfaces rather than only broad umbrella notes
- Risks / rollback: additive note batch only; structural work is effectively complete and remaining work is mostly stub replacement or optional deepening
- Follow-up:
  - [ ] Replace stub-heavy external captures when upstream docs stabilize
  - [ ] Add only optional deeper notes if a specific maintenance lane starts seeing repeated use

### [2026-04-17 00:38] Strict Source-Complete Roadmap
- Mode: derive
- Summary: Added a maintained roadmap note that consolidates the remaining strict scratch-from-zero execution plan into slices, waves, and subagent workstreams.
- `raw`: unchanged
- `wiki`: added `wiki/topics/strict-source-complete-roadmap.md`; updated `wiki/index.md`
- `indexes`: updated `indexes/coverage.md`
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged; roadmap note points back to support-matrix, audit, workflow, orchestrator, and docs surfaces as authorities
- `provenance`: linked the roadmap to canonical code, generated contract surfaces, and current local support-matrix output
- `derived output`: none
- `vault`: frontmatter added for one new maintained topic note; no shared `.obsidian/` surfaces changed
- `path map`: none
- `link/backlink impact`: wiki home and coverage index now expose a canonical route for strict-completeness execution planning
- Risks / rollback: additive KB note only; rollback is limited to removing the note and index/log references
- Follow-up:
  - [ ] Start Wave A from the roadmap: season-type contract, registry/artifact truth cleanup, and live snapshot contract design

### [2026-04-22 13:45] KB Repair and Control-Plane Extension
- Mode: improve
- Summary: Repaired the KB trust layer, refreshed repo-path references to the current docs tree, added control-plane/live-snapshot coverage, and tightened the tracked vault surface with a KB-local ignore file.
- `raw`: added `endpoint-coverage-and-audit-manifest`, `docs-generator-manifest`, and `full-extraction-control-manifest`; refreshed existing internal manifests to current docs/chat note targets
- `wiki`: added `wiki/topics/full-extraction-control-plane.md` and `wiki/topics/live-snapshot-contract.md`; refreshed `docs-autogen`, `docs-profiling-surface`, `model-audit`, `endpoint-coverage-source-summary`, `lineage-internals`, and route/model/ops docs-path references
- `indexes`: refreshed `canonical-material`, `docs-surface-map`, `ingest-queue`, `source-map`, `coverage`, `topic-family-map`, `internal-source-catalog`, and `wiki/index.md`
- `schema`: unchanged
- `config`: unchanged; `obsidian-vault-conventions` now records the same-batch maintenance rule for `coverage`, `source-map`, `source_count`, and `activity/log.md`
- `canonical material`: removed dead `CLAUDE.md` references and aligned public-docs paths to the current `start/`, `ops/`, `model/`, and `sources/` layout
- `provenance`: linked the new control-plane and docs-generator bridges into maintained topic notes and removed dead local-path refs except the intentionally optional `docs/table-profile.generated.json`
- `derived output`: none
- `vault`: added `kb/.gitignore` plus tracked `.obsidian/snippets/.gitkeep`; local validators now only warn about the still-present volatile `.obsidian/{app,graph,workspace}.json` files if they remain in the working tree
- `path map`: docs-path refresh from legacy `guides/` / `schema/` / `lineage/` note references to current `start/` / `ops/` / `model/` / `sources/` surfaces
- `link/backlink impact`: `coverage` now has one concrete row per maintained wiki page, `source-map` source IDs are unique, and the KB has first-class routes for full-extraction control flow and live-snapshot semantics
- Risks / rollback: broad KB-only edit batch; rollback can be done by removing the new manifests/notes and restoring the refreshed indexes and path refs
- Follow-up:
  - [ ] Replace or delete the untracked local `.obsidian/app.json`, `.obsidian/graph.json`, and `.obsidian/workspace.json` files if the repo should never carry them in the working tree
  - [ ] Keep future KB growth narrow and admit it only with same-batch index/log maintenance

### [2026-04-22 16:20] KB Refactor-Alignment Wave
- Mode: improve
- Summary: Aligned the remaining KB docs-path and chat-runtime notes to the live worktree so the companion vault now treats `src/nbadb/chat/*` as the canonical shared runtime, `chat/` as the app shell plus compatibility entrypoint layer, and `docs/content/docs/model/*` as the canonical model-docs tree.
- `raw`: no new extracts; refreshed source-map routing so the existing internal manifests point at the notes they now back
- `wiki`: patched lineage/docs-path notes, helper/runtime notes, and KB home routing; added source-boundary discoverability for `upstream-nba-api` and `extraction-boundary`
- `indexes`: refreshed `coverage`, `source-map`, `skill-surface-map`, `internal-source-catalog`, `topic-family-map`, and `canonical-material`
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: replaced stale legacy docs-tree references with `docs/content/docs/model/{schema,dictionary,diagrams,lineage}` where those are now canonical
- `provenance`: replaced `chat/server/*`-first citations with `src/nbadb/chat/*` canonical paths except where the wrapper/shim boundary itself is materially true
- `derived output`: none
- `vault`: unchanged
- `path map`: helper/runtime notes now distinguish canonical shared runtime paths from compatibility wrappers and app-shell entrypoints
- `link/backlink impact`: `coverage` now includes the upstream/extraction notes and refreshed chat/runtime rows; `source-map` now points the extractor and chat manifests at the maintained notes they support
- Risks / rollback: KB-only prose/index batch; rollback is a straight revert of the touched `kb/` files
- Follow-up:
  - [ ] Keep future note additions narrow and continue updating `coverage`, `source-map`, `source_count`, and `activity/log.md` in the same batch

### [2026-05-07 15:15] Runbook Registry Repair
- Mode: improve
- Summary: Integrated the runbook registry into maintained KB navigation and repaired stale local and docs-path references found by Nerdbot lint.
- `raw`: unchanged
- `wiki`: updated `wiki/operations/runbooks.md` and `wiki/index.md`
- `indexes`: updated `indexes/coverage.md` and `indexes/source-map.md`
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged; docs and repo command paths remain authoritative
- `provenance`: replaced dead governance references with existing KB config surfaces and refreshed public docs guide paths
- `derived output`: none
- `vault`: updated frontmatter `updated` values only; no aliases, embeds, or shared `.obsidian/` surfaces changed
- `path map`: none
- `link/backlink impact`: `wiki/operations/runbooks.md` now has an inbound link from `wiki/index.md`; broken related-index wikilinks were replaced with existing maintained indexes
- Risks / rollback: low-risk KB-only repair; rollback is a straight revert of the touched KB files
- Follow-up:
  - [ ] Refresh the already-modified Kaggle KB pages, coverage timestamps, and activity entry once the current Kaggle code/docs changes are finalized
  - [ ] Consider broad docs-path synthesis refresh as a separate batch if old `docs/content/docs/start/` or `ops/` references still matter

### [2026-05-07 15:35] Kaggle Lane Follow-through
- Mode: improve
- Summary: Integrated the already-modified Kaggle distribution and publishing notes into the maintained coverage ledger without changing their article bodies.
- `raw`: unchanged
- `wiki`: unchanged in this batch; pre-existing edits remain in `wiki/operations/kaggle-distribution.md` and `wiki/topics/kaggle-publishing-lane.md`
- `indexes`: refreshed `indexes/coverage.md` review dates and backing-material summaries for the two Kaggle pages
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged; Kaggle CLI/docs/code remain authoritative
- `provenance`: coverage now records metadata/client implementation and published-example linkage as backing material for the updated notes
- `derived output`: none
- `vault`: unchanged
- `path map`: none
- `link/backlink impact`: no new note links; this is ledger follow-through for existing maintained pages
- Risks / rollback: low-risk index/log batch; rollback is a straight revert of `coverage.md` and this log entry

### [2026-05-07 15:40] Docs Topology Refresh
- Mode: improve
- Summary: Refreshed the central docs-surface map, docs-source summary, raw docs inventory, canonical-material ledger, ingest queue, KB home provenance, and route coverage rows to match the live docs tree under root pages, reference sections, endpoints, lineage, and guides.
- `raw`: updated `raw/extracts/internal/docs-surface-inventory.md`
- `wiki`: updated `wiki/topics/docs-site-source-summary.md` and `wiki/index.md`
- `indexes`: updated `indexes/docs-surface-map.md`, `indexes/ingest-queue.md`, `indexes/canonical-material.md`, and route rows in `indexes/coverage.md`
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged; `docs/content/docs/meta.json` and the current docs tree remain authoritative
- `provenance`: replaced central stale `start`, `ops`, `model`, and `sources` topology claims with current root/reference/guides/endpoints paths
- `derived output`: none
- `vault`: updated frontmatter `updated` values only on docs-source notes
- `path map`: central docs path synthesis now points to `schema/`, `data-dictionary/`, `diagrams/`, `endpoints/`, `lineage/`, `guides/`, and root getting-started pages
- `link/backlink impact`: no new wiki pages; central evidence pages now reduce future stale-path propagation
- Risks / rollback: KB-only synthesis refresh; rollback is a straight revert of the touched KB files
- Follow-up:
  - [ ] Refresh older per-topic route/model docs-path mentions in smaller future batches rather than broad-replacing every stale path at once

### [2026-05-07 15:45] Vault Ignore Hygiene
- Mode: improve
- Summary: Expanded the KB-local ignore rules so nested macOS `.DS_Store` files stay out of the vault regardless of where Finder creates them.
- `raw`: unchanged
- `wiki`: unchanged
- `indexes`: unchanged
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged
- `provenance`: unchanged
- `derived output`: none
- `vault`: updated `kb/.gitignore`; existing local `.DS_Store` files were not deleted in this batch
- `path map`: none
- `link/backlink impact`: none
- Risks / rollback: low-risk ignore-only change; rollback is a straight revert of `kb/.gitignore` and this log entry

### [2026-09-19 02:00] Database Conventions Note
- Mode: improve
- Summary: Added `wiki/topics/database-conventions.md`, a warehouse-lifecycle and conventions reference (pipeline tables, staging keys, star families, validation tiers, exports, scan gate, Kaggle-seeding path), grounded in source-line citations and the 2026-09-19 Kaggle v238 bundle observation.
- `raw`: unchanged
- `wiki`: added `wiki/topics/database-conventions.md`; linked it from the Warehouse model area in `wiki/index.md`
- `indexes`: added a coverage row in `indexes/coverage.md`
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged; `src/nbadb/`, `README.md`, and `AGENTS.md` remain authoritative
- `provenance`: note carries a Provenance table; bundle observations are dated and marked as freshness triggers
- `derived output`: none
- `vault`: updated frontmatter per topic-note conventions
- `path map`: none
- `link/backlink impact`: one new wiki page with inbound links from `wiki/index.md` and `indexes/coverage.md`
- Risks / rollback: KB-only additive batch; rollback is a straight revert of the three touched KB files

### [2026-09-19 02:40] Full Extraction Requirements Note
- Mode: improve
- Summary: Added `wiki/operations/full-extraction-requirements.md`, the human prerequisites for dispatching the CI full-extraction workflow: Nord-only VPN provider contract (with dated Mullvad incompatibility verdict), credential modes and secrets, dispatch inputs, fork Actions activation, and the `network_mode=direct` no-credential fallback.
- `raw`: unchanged
- `wiki`: added `wiki/operations/full-extraction-requirements.md`; linked from `runbooks.md` (new "Full Extraction (CI)" section) and the Operations line in `wiki/index.md`
- `indexes`: added a coverage row in `indexes/coverage.md`
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged; `.github/workflows/full-extraction.yml`, `.github/actions/nordvpn-connect/`, and `AGENTS.md` remain authoritative
- `provenance`: note carries a Provenance table; fork/runtime observations and the NordVPN connection limit are dated and marked as freshness triggers
- `derived output`: none
- `vault`: updated frontmatter per topic-note conventions
- `path map`: none
- `link/backlink impact`: one new wiki page with inbound links from `runbooks.md`, `wiki/index.md`, and `indexes/coverage.md`
- Correction (same session): `targeted_smoke` reworded to direct-only per the actual workflow guard (`full-extraction.yml:321-339`); `AGENTS.md` "VPN-only" wording flagged stale; secrets guidance refined to recommend all three (configured pair + token fallback, `connect.py:894-930`)
- Risks / rollback: KB-only additive batch; rollback is a straight revert of the four touched KB files

### [2026-09-19 07:30] Full Extraction Requirements: Plan-Gate Contract Expansion
- Mode: improve
- Summary: Extended `wiki/operations/full-extraction-requirements.md` (did not create a parallel note) with the mode-validation constraint set (`direct_parallelism=0` requirement for `network_mode=vpn`, observed run `35428015854`) and a new "Plan gate: support-matrix and adequacy-scorecard contract" section covering both `plan`-job gates (`full-extraction.yml:466-563`) and the `transform_contract_missing` misclassification found and fixed in run `35428089035`: eight authored `compatibility_reference_only` endpoints (six `box_score_*_v2` aliases, `league_standings_legacy`, `play_by_play_legacy`) were flagged with a blocking gap despite an explicit maintainer disposition that they have no star-schema consumer by design.
- `raw`: unchanged
- `wiki`: expanded `wiki/operations/full-extraction-requirements.md` (mode-validation note, corrected dispatch example, new plan-gate section, three new provenance rows)
- `indexes`: updated the `full-extraction-requirements.md` row in `indexes/coverage.md`
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged; `.github/workflows/full-extraction.yml` and `src/nbadb/core/endpoint_coverage.py` remain authoritative
- `provenance`: three new line-anchored rows added; `source_count` bumped 8 → 11
- `derived output`: none
- `vault`: frontmatter `source_count` updated; `updated` date unchanged (already 2026-09-19)
- `path map`: none
- `link/backlink impact`: no new pages; existing inbound links from `runbooks.md`/`wiki/index.md`/`indexes/coverage.md` unaffected
- Companion source change: `src/nbadb/core/endpoint_coverage.py` gap classification fixed (compatibility_reference_only rows no longer emit `transform_contract_missing` when `transform_outputs` is empty); `tests/unit/core/test_endpoint_coverage.py` assertions for `player_vs_player`/`video_status` updated to match; full `tests/unit/core` suite green (676 passed, 2 skipped)
- Risks / rollback: KB-only additive batch; rollback is a straight revert of the two touched KB files (source fix tracked separately in git)

### [2026-09-19 08:15] All-Time Leaders Transform: Close Remaining Unmodeled Categories
- Mode: fix (source-only; no KB note materially expanded)
- Summary: Follow-on to the `transform_contract_missing` classification fix above. After that fix, `nbadb audit-models --mode inventory --strictness consistency --require-result-table-contract` still reported 17 `unowned` staging entries, all `stg_all_time_*` result sets: `AllTimeLeadersGrids` returns 19 stat-category result sets but `agg_all_time_leaders` (`src/nbadb/transform/derived/agg_all_time_leaders.py`) only ever consumed 3 (`pts`, `ast`, `reb`). Confirmed this was genuinely unmodeled data (not a duplicate/alias) by inspecting `staging_map.py:2214-2293` and a raw audit row; user decided to extend the transform to all 19 categories rather than author a `compatibility_reference_only` exemption.
- `raw`: unchanged
- `wiki`: unchanged (no note edited)
- `indexes`: updated the `full-extraction-requirements.md` row in `indexes/coverage.md` (backing-material and notes columns) to record the companion fix
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: `src/nbadb/transform/derived/agg_all_time_leaders.py`, `src/nbadb/schemas/star/agg_schemas.py`, `src/nbadb/core/endpoint_coverage.py` remain authoritative
- `provenance`: none (no note touched)
- `derived output`: none
- `vault`: none
- `path map`: none
- `link/backlink impact`: none
- Companion source change: `agg_all_time_leaders.py` rewritten to generate one CTE pair per stat category (SQL built programmatically via a category-loop helper, not hand-duplicated), still `FULL OUTER JOIN`ing all 19 categories on `player_id`/`player_name` with a `conflicting player names` error guard; `agg_schemas.py`'s `AggAllTimeLeadersSchema` extended with the 16 new value/rank column pairs; added a `stg_all_time` → `compatibility_reference_only` disposition in `_MODEL_OWNERSHIP_STAGING_KEYS` for the legacy pre-fix alias staging key (`stg_all_time_ast`/`_pts`/`_reb` sourced via `stg_all_time` before the multi-result-set staging split — retained as a documented compatibility surface, not reachable by any transform). Discovered and fixed an unrelated static-analysis gotcha while editing: `SqlTransformer.depends_on` built via a set/list comprehension over an f-string is invisible to the AST-based `_constant_string_list` discovery helper in `endpoint_coverage.py`; replaced with an explicit literal list (matches the pattern every other transformer already uses). `tests/unit/transform/test_derived_transformers.py` extended (18 new pytest cases covering all-19-category dependency declaration, disjoint-category FULL OUTER JOIN correctness, null player-id fail-closed behavior, and schema coverage); local `audit-models`/`extract-completeness --require-model-contract` gates both pass with `unowned=0`; full `tests/unit/transform`, `tests/unit/schemas`, `tests/unit/orchestrate`, `tests/unit/cli`, and `tests/unit/core/test_endpoint_coverage.py` suites green.
- Risks / rollback: source-only batch; rollback is `git revert` of the four touched `src/`/`tests/` files plus this log entry and the coverage-index row edit.

### [2026-09-19 09:00] Full Extraction: Diagnosed extract-stage hang as HTTP client TLS/fingerprint block
- Mode: diagnosis (KB note materially expanded; no source fix — remediation needs a maintainer decision)
- `wiki`: expanded `operations/full-extraction-requirements.md` with a new "Root cause"
  section
- `indexes`: updated the `full-extraction-requirements.md` row in `indexes/coverage.md`
  (backing-material and notes columns)
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: `nba_api/stats/library/http.py` (installed package, exact pinned
  version), `.github/actions/nordvpn-connect/connect.py` remain authoritative
- `provenance`: added one row citing the dedicated `Debug NBA Probe` workflow's run
  history and the exact `nba_api` HTTP client file/lines
- `derived output`: none
- `vault`: none
- `path map`: none
- `link/backlink impact`: none
- Summary: dispatched the fixed-commit full extraction (`35430687683`); `plan` passed for
  the first time ever, but `preflight` failed extraction with a `ConnectionError` on the
  first real extractor call (`common_all_players`) despite a clean, verified OpenVPN
  connection and passing lightweight control-plane/NBA-Stats curl probes. Built a
  throwaway `Debug NBA Probe` workflow plus `.github/scripts/debug_common_all_players.py`
  / `debug_raw_http.py` to bisect the variable; ran season-isolated retries, a raw-socket
  bypass of the extractor stack, curl-vs-`requests` comparisons, and finally an
  interleaved same-session A/B loop (6 rounds each). Result: `curl` succeeds 6/6 on both
  a control endpoint and the failing target endpoint, over the identical tunnel and exit
  IP, interleaved with 6/6 `requests`/urllib3 failures on the same target endpoint. This
  is airtight evidence of an HTTP-client TLS/fingerprint block at NBA's edge, not a VPN,
  DNS, throttling, or timing issue — and since every one of the 162 registered
  extractors goes through `nba_api`'s `requests`-based `NBAStatsHTTP`, it blocks all
  VPN-routed extraction unconditionally.
- Risks / rollback: KB-only additive batch; rollback is a straight revert of the two
  touched KB files. The three throwaway debug files were committed then deleted in the
  same session (`cc2b61c`..`55e78e1` added, later commit removes them) — no functional
  source touched, `tests/unit` and `tests/unit/core/test_endpoint_coverage.py` unaffected.
- Open decision for the user: how to remediate the transport-layer block (e.g. swap in a
  TLS/HTTP2 fingerprint-impersonating client such as `curl_cffi` for `nba_api`'s session)
  without breaking the pinned `nba_api 1.11.4` contract or `STATS_HEADERS` parity tests —
  not resolved in this session; see the note's "Root cause" section.

### [2026-09-19 09:30] TLS Fingerprint Mitigation Research: New Note
- Mode: research capture (new maintained note; no source, test, or workflow changes)
- `raw`: unchanged (research drew on external primary sources only — official
  `curl_cffi`/`curl-impersonate`/`tls-client`/`httpx` PyPI+GitHub metadata, official
  Cloudflare JA3/JA4 docs, `nba_api` GitHub issue tracker — none captured into `raw/`)
- `wiki`: added `wiki/topics/tls-fingerprint-mitigation.md`; expanded
  `wiki/operations/full-extraction-requirements.md`'s "Root cause" section to link it
  instead of restating the alternatives inline
- `indexes`: added a row for the new note to `indexes/coverage.md`
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: `nba_api` `stats/library/http.py` and `library/http.py`
  (installed `.venv`, exact tag `v1.11.4`) remain authoritative; the new note's
  third-party client claims are dated PyPI/GitHub metadata observations, not repo canon
- `provenance`: new note carries its own full provenance table (14 sources); the parent
  note's provenance table gains no new row, only the cross-link
- `derived output`: none
- `vault`: new note's frontmatter initialized (`kind: concept`, `status: active`,
  `source_count: 14`); no shared `.obsidian/` surfaces touched
- `path map`: none
- `link/backlink impact`: one new wiki page with an inbound link from
  `operations/full-extraction-requirements.md`'s "Root cause" and "Related notes"
  sections; `indexes/coverage.md` gains the matching row
- Summary: Spawned a background research agent to investigate mitigations for the
  `requests`/urllib3 TLS/HTTP2 fingerprint block diagnosed against `nba_api==1.11.4`'s
  `NBAStatsHTTP` client (prior entry above). Findings: primary-source evidence on JA3/JA4
  fingerprinting, a ranked comparison of `curl_cffi`, `curl-impersonate`, `tls-client`,
  `httpx`, and other candidates against nbadb's exact `_ThreadLocalSessionMixin`
  integration contract, and a recommended approach (`curl_cffi`'s
  `requests.Session(impersonate=...)` drop-in) with an implementation sketch — no code
  changed.
- Companion source change: none (research-only; no repository behavior touched).
- Risks / rollback: additive KB-only batch (one new file, two small edits to existing KB
  files); rollback is a straight revert.
- Still open: the maintainer decision on which transport to adopt, and the actual
  implementation, remain unresolved — this batch only supplies the evidence base.

### [2026-09-19 16:20] Implemented curl_cffi transport swap (TLS fingerprint mitigation)
- Mode: improve
- Summary: Landed the remediation the prior two batches researched — nbadb's session
  factory now returns a `curl_cffi` `_PinnedTransportSession` (browser-fingerprinted
  TLS/HTTP-2, `default_headers=False`, `retry=0`, `verify=certifi.where()`), with
  requests-compatible query-parameter encoding, in-code no-ambient-proxy enforcement
  (`trust_env` is inert in curl_cffi; `proxies={"all": ""}` restores the old contract),
  `certifi` promoted to a direct dependency, and curl transport-layer fault names
  classified `transport_transient` in `nbadb.core.extraction_failures`.
- `raw`: unchanged
- `wiki`: `wiki/topics/tls-fingerprint-mitigation.md` (implemented-remediation section,
  decisions taken incl. deliberate `chrome`-alias deviation, verification record,
  refreshed line anchors)
- `indexes`: `indexes/coverage.md` (topic row moved from "recommends … no
  implementation performed" to implemented status)
- `schema`: unchanged (`SAFE_ROOT_ERROR_NAMES` untouched; curl fault names map onto
  existing safe roots, so `root_exception_class`'s `isin` constraint is stable)
- `config`: unchanged
- `canonical material`: annotated (installed `curl_cffi` 0.16.3 sources inspected for
  the `trust_env` inertness, CA-default, and proxy-application findings; provenance
  rows in the topic note unchanged)
- `derived output`: none
- `vault`: no frontmatter/alias/embed changes; no shared `.obsidian/` surfaces touched
- Companion source change: `src/nbadb/extract/nba_api_adapter.py`,
  `src/nbadb/core/extraction_failures.py`, `pyproject.toml` + `uv.lock` (certifi),
  `tests/unit/extract/test_nba_api_adapter.py` (session test replaced, red/green
  verified), `tests/unit/core/test_extraction_failures.py` (curl-code cases).
- Risks / rollback: revert the adapter+classifier commits to return to the `requests`
  transport (which is fingerprint-blocked upstream — rollback only makes sense paired
  with a different mitigation); the KB edits revert independently.
- Still open: live confirmation through the CI VPN lane (local runs cannot reach
  `stats.nba.com` from this network); then the full-extraction dispatch itself.

### [2026-09-19 18:30] Preflight canary: header-permutation root cause, empty-rejection revert
- Mode: enrich
- Summary: The preflight discovery canary's `failure_kind=empty` was not a VPN exit-IP
  soft block but a `commonallplayers` header permutation demoting a complete 582-row
  response to a lossless fallback; fixed at the contract boundary, reverted the
  server-rotation misdiagnosis, and recorded the wider pinned-contract staleness.
- `raw`: none
- `wiki`: `wiki/operations/full-extraction-requirements.md` (new root-cause section,
  pinned-contract staleness sweep, corpus-rebind procedure, six provenance rows)
- `indexes`: `indexes/coverage.md` (row refreshed for the note above)
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged
- `provenance`: run `35469167028` preflight log, local residential-IP repro, a 24-endpoint
  live drift sweep, and the `swar/nba_api` `v1.11.4` clone (HEAD `e0295f83`) are all
  linked in the note's provenance table
- `derived output`: none
- `vault`: no frontmatter/alias/embed changes; no shared `.obsidian/` surfaces touched
- Companion source change: `src/nbadb/extract/nba_api_adapter.py` (permutation admitted in
  `_strict_stats_packets`), `.github/scripts/probe_discovery_transport.py`
  (`contract_drift` kind), `.github/actions/nordvpn-connect/connect.py` (revert `f2ba74a`;
  sanitize the `63f1559` attestation dump, which was leaking unrecognized
  `root_error_type` content into run logs), plus the three test files and a star semantic
  corpus rebind (five of seven pins moved).
- `link/backlink impact`: none; section added inside an existing note
- Risks / rollback: reverting the adapter commit restores strict positional header
  matching and re-breaks the canary; the KB edits revert independently.
- Follow-up:
  - [ ] Decide the contract authority for columns NBA serves but nba_api does not
        document (`player_game_logs`, `player_index`, `all_time_leaders_grids`,
        `draft_history`) — deferred, not closed.
  - [ ] `NBA_STACK_PROBE_DEFAULT_SEASON` is pinned to `2024-25` while `current_season()`
        is `2025-26`; the canary passes either way but returns a degenerate 136 rows on
        the stale season.
  - [ ] Six pre-existing `tests/unit/contracts` failures confirmed unrelated to this work
        (identical on the pre-change tree); still unidentified.

### [2026-09-19 19:40] discovery_seed: local observation pin for undocumented provider columns
- Mode: enrich
- Summary: `discovery_seed` failed in run `35476517060` because `player_game_logs` (its
  primary player/team source) and `player_index` (its fallback) were both zero-width from
  `additive_header`; resolved with a dated local pin admitting only the columns NBA is
  observed to serve that nba_api v1.11.4 does not document.
- `raw`: none
- `wiki`: `wiki/operations/full-extraction-requirements.md` (deferral reversed; pin
  contract, optional-column semantics and freshness trigger documented; four provenance
  rows)
- `indexes`: unchanged (coverage row already points at this note)
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged
- `provenance`: run `35476517060` discovery_seed log, local per-season header diffs, and a
  post-pin 36-call sweep reporting zero drift
- `derived output`: none
- `vault`: no frontmatter/alias/embed changes; no shared `.obsidian/` surfaces touched
- Companion source change: `src/nbadb/core/nba_api_observed_columns.py` (new),
  `src/nbadb/extract/nba_api_adapter.py` (`_expected_result_sets` widens by the admitted
  delta, resolved against the observed response),
  `tests/unit/core/test_nba_api_observed_columns.py` (new), plus a second star semantic
  corpus rebind (the same five pins moved again).
- `link/backlink impact`: none
- Risks / rollback: reverting the pin module and the `_expected_result_sets` change
  restores the generated-contract-only behaviour and re-blocks `discovery_seed`. The pin
  is additive-only and closed, so it cannot mask a removal or an unenumerated addition.
- Follow-up:
  - [ ] Re-derive the admitted-columns table on any `nba-api` upgrade and delete entries
        upstream has caught up with; the guard test fails if one goes stale.
  - [ ] Consider upstreaming the missing endpoint docs to `swar/nba_api` so the pin can
        eventually be retired.

### [2026-09-19 20:55] vpn_capacity barrier + nine more observed-column pins
- Mode: enrich
- Summary: `discovery_seed` passed for the first time; `vpn_capacity` slot 0 then died on a
  transient GitHub artifact-listing inconsistency, which the barrier treated as fatal.
  Made that one condition retryable, and extended the observed-column pin to nine more
  endpoints that `extract` reaches in waves 0-3.
- `raw`: none
- `wiki`: pending (note update deferred to the next batch)
- `indexes`: unchanged
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged
- `provenance`: run `35482387144` (preflight and discovery_seed green; vpn_capacity slot 0
  log), lane manifest wave analysis, and a 101-endpoint ID-requiring drift sweep
- `derived output`: none
- `vault`: unchanged
- Companion source change: `.github/scripts/vpn_control_plane.py` (new
  `ArtifactInventorySnapshotError`, retried inside `wait_for_capacity_markers` only),
  `src/nbadb/core/nba_api_observed_columns.py` (nine endpoints added),
  `tests/unit/orchestrate/test_vpn_control_plane.py` (three tests).
- Risks / rollback: reverting the barrier change restores fail-on-inconsistency, which is
  a coin-flip per run. The retry keeps the same 780s timeout and the same final assertion,
  and a non-snapshot GitHubApiError still aborts immediately.
- Follow-up:
  - [ ] `common_player_info` and `team_info_common` are broken two ways and were left
        alone: their pinned result sets sort `AvailableSeasons` to canonical index 0, so
        `_from_nba_api` validates a one-column frame. Fixing it means editing
        `extract/stats/player_info.py` and `extract/stats/team_info.py`, which are frozen
        by the implicit-competition source authority and need a governed re-issue
        (three independent roots, author role, predecessor receipt). Their pin entries
        were removed so behaviour is unchanged rather than worse.
  - [ ] 16 endpoints in `extract` waves 2-5 drift with `removed_header`, which an
        additive-only pin cannot express. Needs its own authority decision.
  - [x] The two shot-location endpoints: resolved. They are ordinary additive drift
        (`corner_3_fgm/fga/fg_pct`, plus `NICKNAME` on the player variant); the earlier
        "needs separate analysis" reading was a measurement error from a naive header
        flatten. Both are now pinned.

### [2026-09-19 21:25] Extract-phase drift survey and scope correction
- Mode: enrich
- Summary: Swept the 101 ID-requiring endpoints the first survey could not reach, pinned
  the two shot-location endpoints after correcting a measurement error, and established
  that remaining drift costs completeness rather than pipeline liveness.
- `raw`: none
- `wiki`: `wiki/operations/full-extraction-requirements.md` (two new sections: what the
  remaining drift costs, and the extract-lane drift inventory; seven provenance rows)
- `indexes`: unchanged
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged
- `provenance`: 101-endpoint live sweep, lane manifest of run `35476517060`, workflow
  job-gating lines, and live-vs-pinned header diffs for the named endpoints
- `derived output`: none
- `vault`: unchanged
- Companion source change: `src/nbadb/core/nba_api_observed_columns.py` (shot-location
  entries; 13 endpoints pinned in total).
- `link/backlink impact`: none
- Risks / rollback: the two new pin entries revert independently; they are additive-only
  and optional, so removing them restores the prior zero-width behaviour.
- Follow-up:
  - [ ] `team_details` needs whole-result-set admission (`TeamAwardsCommCup`), which the
        column-level pin cannot express.
  - [ ] Verify the fixture-based sweep against real lane behaviour once `extract` runs;
        27 drifting is an upper bound and at least one hit was parameter-sensitive.

### [2026-09-19 22:15] Extract reached; two stacked workflow defects fixed
- Mode: enrich
- Summary: The chain reached `extract` for the first time. All 256 lanes died in `Set up
  job` on a 39-character `download-artifact` SHA pin; fixing that exposed `lane_control`
  calling `resume` without its required `--operation-authority-path`, which would have
  stopped the chain even with a green extract.
- `raw`: none
- `wiki`: `wiki/operations/full-extraction-requirements.md` (new section on the two
  workflow defects; corrected the earlier completeness-vs-liveness claim; three
  provenance rows)
- `indexes`: unchanged
- `schema`: unchanged
- `config`: unchanged
- `canonical material`: unchanged
- `provenance`: run `35484551473` extract and lane_control logs, a repo-wide `uses:` SHA
  length audit, and `full_extraction_control.py:9764`
- `derived output`: none
- `vault`: unchanged
- Companion source change: `.github/workflows/full-extraction.yml` (`a3d2cc5` pin repair,
  `53b6f2e` operation-authority argument).
- `link/backlink impact`: none
- Risks / rollback: both changes are single-purpose and revert independently.
- Correction: an earlier entry claimed drift costs completeness rather than liveness,
  reasoning that downstream jobs run on `always()`. They do start on `always()`, but also
  require `needs.lane_control.result == 'success'`, and `lane_control` failing skipped
  `checkpoint`, `merge` and `dispatch_next`. The blast radius of a *partial* lane failure
  remains unmeasured.
- Follow-up:
  - [ ] Measure whether `lane_control` tolerates partial lane failure; run `35484551473`
        failed 256/256 and so cannot distinguish that from an all-green requirement.
  - [ ] Consider a CI guard asserting every `uses:` SHA pin is exactly 40 hex characters.
