---
title: Database Conventions
tags:
  - kb
  - topics
  - database
  - warehouse
aliases:
  - nbadb Database Conventions
kind: concept
status: active
updated: 2026-09-19
source_count: 16
---

# Database Conventions

How a checkout becomes a queryable local warehouse, how that warehouse is layered, and the
conventions (pipeline tables, staging keys, star families, validation tiers, exports) that
hold it together. Written for maintainers and agents; every claim cites canon under
`src/nbadb/`, `README.md`, or `AGENTS.md`.

## From empty checkout to a queryable database

Three documented paths, ordered slowest/most complete first:

1. **Full local build** — `nbadb init` (or `uv run nbadb init --season-start 1946` from a
   checkout). Full historical build, 1946-present; resume-safe via journal/checkpoint
   state; runtime is bounded by upstream endpoint availability and throttling.
   (`README.md:64-70`, `AGENTS.md:126-151`)
2. **Refresh of an existing warehouse** — `nbadb daily` (~5-15 min) or `nbadb monthly`;
   targeted repair via `nbadb backfill run` (`README.md:86-89`, `AGENTS.md:141-143`).
3. **Kaggle download** — `nbadb download` pulls the published dataset and seeds local
   DuckDB without any extraction (`README.md:95`, `src/nbadb/cli/commands/download.py:54`).
   The assured variant, `nbadb download --verified-public-baseline --dataset-version N`,
   installs one exact version after full SHA-256 readback (`download.py:18-31`).

`nbadb migrate` only provisions the 10 internal pipeline tables, not data
(`src/nbadb/cli/commands/migrate.py:11-15`).

Settings that anchor every path: `NbaDbSettings` (env prefix `NBADB_`) defaults
`data_dir=data/nbadb`, formats `[sqlite, duckdb, csv, parquet]`,
`kaggle_dataset=wyattowalsh/basketball`, with derived `sqlite_path`/`duckdb_path` and a
`@lru_cache`d `get_settings` (`src/nbadb/core/config.py:10-21,203-219`).

## Warehouse lifecycle

`extract (raw_*) -> STAGING_MAP stg_* staging tables in DuckDB -> TransformPipeline
(schemas/star) -> dim_/fact_/bridge_/agg_/analytics_ -> MultiLoader export to
sqlite/duckdb/csv/parquet`. Pipeline state lives in the 10 underscore-prefixed DuckDB
tables below (`AGENTS.md:30-39` module map; `src/nbadb/orchestrate/orchestrator.py:14-60`
wires DBManager + TransformPipeline + `create_multi_loader`).

## Internal pipeline tables (10)

Created by `DBManager._create_pipeline_tables()` (`src/nbadb/core/db.py:737`, called at
`:689`); the same ten are listed in `AGENTS.md:201-215`. User-table walks exclude them via
an `_%` filter (`core/db.py:1139-1146`, `orchestrate/scanner.py:627-628`).

`_pipeline_watermarks` `db.py:741`, `_extraction_journal` `:751`, `_pipeline_metadata`
`:801`, `_pipeline_metrics` `:813`, `_transform_checkpoints` `:823`, `_schema_versions`
`:832`, `_schema_version_history` `:842`, `_transform_metrics` `:852`, `_lane_metrics`
`:866`, `_staging_chunk_journal` `:884`.

## Naming families and registries

Conventions are registry-driven, not hand-listed:

- **Staging**: `STAGING_MAP: list[StagingEntry]` (`src/nbadb/orchestrate/staging_map.py:258`)
  is the authority; the DuckDB table name is `entry.staging_key` (e.g. `stg_league_game_log`
  `:260`). Conditional lossless keys `stg_nba_api_live_lossless_nodes` /
  `stg_nba_api_lossless_result_cells` are published only when drift is observed
  (`staging_map.py:29-36`).
- **Raw/staging/star schemas**: auto-discovered by module+prefix —
  `_discover_schemas(..., class_prefix="Staging", table_prefix="stg_")`
  (`src/nbadb/schemas/registry.py:186-190`); star schemas discovered with an empty prefix
  (`registry.py:198-202`); input/output lookups `get_input_schema` `:191`,
  `get_output_schema` `:207`; route-count contract bound at
  `contracts/staging_route_contract.py:88`.
- **Star families**: `dim_` (18) / `fact_` (204) / `bridge_` (6) / `agg_` (19) /
  `analytics_` (14) per `AGENTS.md:64-72`; the allowed family set is enforced by
  `contracts/transform_output_disposition_authority.py:70-72` and classified by
  `core/schema_annotations.py:494-498`. Builders live under
  `transform/{dimensions,facts,derived,views,live}`.

## Three-tier Pandera validation

One `BaseSchema.validate()` (`src/nbadb/schemas/base.py:194-268`; `strict=False`) called
at three seams: **raw** inside extract/live
(`extract/raw_schema_registry.py:55`, `orchestrate/live_snapshot.py:924`), **staging** as
transform input (`transform/pipeline.py:222` via registry), **star** as transform output
(`transform/pipeline.py:266`). Raw/staging preserve extra columns; star projects to the
declared schema (`AGENTS.md:78-85`).

## Export surface

`BaseLoader.load(table, df, mode)` (`src/nbadb/load/base.py:10-17`) behind four loaders:
`DuckDBLoader` (Arrow zero-copy for large frames, `duckdb_loader.py:17,29`),
`SQLiteLoader` (ADBC, `sqlite.py:22-30`), `CSVLoader`, `ParquetLoader`
(`PARTITIONED_TABLES` at `parquet_loader.py:16`). `MultiLoader` +
`SUPPORTED_FORMATS={sqlite,duckdb,csv,parquet}` (`load/multi.py:19`); DuckDB failure is
fatal, secondary formats are non-critical (`multi.py:63`). User entry point:
`nbadb export` (`src/nbadb/cli/commands/export.py:10-48`).

## Scan assurance gate

`nbadb scan --fail-on error` exits 1 when any finding reaches the threshold, computed from
all findings independent of the `--severity` display filter
(`src/nbadb/cli/commands/scan.py:52-60,288-291`). Four categories
(`orchestrate/scanner.py:201-205`): `missing_table`, `cross_table` (coverage +
referential integrity, `scanner.py:3697-3847`), `temporal`, `data_quality`.
`--full-publication` adds checkpoint/successor authority gates (`scan.py:113-175`).
Supersedes the deprecated `run-quality` (`AGENTS.md:230`).

## Kaggle bundle contents and local DuckDB seeding

Observed on the published dataset (version **238**, downloaded 2026-09-19): the bundle
contains `nba.sqlite` (2.35 GB, the real data), `csv/` (16 convenience tables),
`dataset-metadata.json`, `run_summary.json`, and `nba.duckdb` as a **12 KB stub with zero
tables** (`data/nbadb/dataset-metadata.json` declares the resources; observed contents in
`data/nbadb/`). The snapshot is the legacy convenience layout — no `parquet/`, no
publication marker, no `dim_`/`fact_`/`agg_` star tables — and its data ends with the
2022-23 season: `game` spans 1946-11-01 through 2023-06-12, with the newest codes being
2022-23 regular (`22022`, 1,230 games) and playoffs (`42022`, 84 games). Treat bundle
shape and freshness as triggers: re-verify both before relying on a download.

Download seeding path: `KaggleClient.download` copies the bundle into the data dir and
calls `_sync_duckdb_after_download` (`src/nbadb/kaggle/client.py:733-767`), which seeds
DuckDB from the downloaded SQLite when the bundle's own `nba.duckdb` is absent, empty, or
unreadable — `_duckdb_has_user_tables` guards the decision (`client.py:1305-1337`), and
`_seed_duckdb_from_sqlite` ATTACHes the SQLite read-only and `CREATE TABLE AS SELECT`s
each table with identifier validation (`client.py:1339-1377`). The documented download
contract in [[wiki/topics/kaggle-publishing-lane|Kaggle Publishing Lane]] describes
exactly this helper; the shipped v238 stub defeated its absence condition until the
2026-09-19 fix below, so re-check that note's contract against the live bundle. Two fixes
landed 2026-09-19 after the shipped path failed against the real bundle:

- table enumeration now uses `duckdb_tables()` over the attached database instead of
  `sqlite_db.sqlite_master`, which DuckDB 1.5.5 does not expose
  (`client.py:1348-1355`; regression test `tests/unit/kaggle/test_client.py:252`);
- an empty or unreadable bundled `nba.duckdb` no longer shadows the SQLite seeding
  (`client.py:1323-1337`; tests `tests/unit/kaggle/test_client.py:182-249`).

The seeded DuckDB mirrors the SQLite convenience tables — it is not the full transformed
warehouse, and catalog-driven `nbadb ask`/`nbadb chat` routes target star-schema tables,
so they cannot serve queries against this mirror (verified 2026-09-19: `nbadb ask` exits
1 with no matching route). Full star-schema coverage comes only from path 1 or 2 above.

## Related notes

- [[wiki/operations/kaggle-distribution|Kaggle Distribution]]
- [[wiki/topics/kaggle-publishing-lane|Kaggle Publishing Lane]]
- [[wiki/model/table-family-guide|Table Family Guide]]
- [[wiki/tooling/duckdb-polars-pandera-stack|DuckDB, Polars, and Pandera in nbadb]]
- [[wiki/topics/extractor-surface|Extractor Surface]]

## Provenance

| Claim or section | Raw or canonical material | Notes |
|------------------|---------------------------|-------|
| documented build/refresh/download paths | `README.md`, `AGENTS.md`, `src/nbadb/cli/commands/download.py` | public quick start + maintainer commands |
| settings defaults and derived paths | `src/nbadb/core/config.py` | `NbaDbSettings`, `get_settings` |
| 10 pipeline tables and `_%` exclusion | `src/nbadb/core/db.py`, `AGENTS.md` | DDL line anchors |
| staging authority and conditional keys | `src/nbadb/orchestrate/staging_map.py` | `STAGING_MAP`, `StagingEntry` |
| schema discovery and family enforcement | `src/nbadb/schemas/registry.py`, `src/nbadb/contracts/transform_output_disposition_authority.py`, `src/nbadb/core/schema_annotations.py` | prefix-driven |
| validation seams | `src/nbadb/schemas/base.py`, `src/nbadb/transform/pipeline.py` | raw/staging/star |
| export fan-out | `src/nbadb/load/multi.py`, `src/nbadb/load/base.py`, loader modules | `SUPPORTED_FORMATS` |
| scan gate semantics | `src/nbadb/cli/commands/scan.py`, `src/nbadb/orchestrate/scanner.py` | categories + exit code |
| Kaggle v238 bundle observation and staleness | `data/nbadb/` (downloaded 2026-09-19), `data/nbadb/dataset-metadata.json` | runtime observation, dated; legacy layout, ends at 2022-23 |
| documented download-lane contract | `kb/wiki/topics/kaggle-publishing-lane.md` | prior maintained note; shipped-bundle drift captured above |
| seeding path and 2026-09-19 fixes | `src/nbadb/kaggle/client.py`, `tests/unit/kaggle/test_client.py` | current line anchors |
