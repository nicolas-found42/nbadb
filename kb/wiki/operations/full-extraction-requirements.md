---
title: Full Extraction Requirements
tags:
  - kb
  - operations
  - full-extraction
  - ci
  - vpn
aliases:
  - Full Extraction Prerequisites
  - CI Extraction Requirements
kind: concept
status: active
updated: 2026-09-19
source_count: 12
---

# Full Extraction Requirements

Use this note when the question is "what must exist before dispatching
`.github/workflows/full-extraction.yml`?" — credentials, secrets, provider contract, and
fork activation. For how the control plane moves lanes through planning, chaining, and
resume once admitted, see [[../topics/full-extraction-control-plane|Full Extraction
Control Plane]].

## Verified environment state (2026-09-19)

- Fork `nicolas-found42/nbadb` is **public** → standard-runner Actions minutes are free.
- Actions API reports `enabled: true`, `allowed_actions: all` — but **zero workflows are
  registered** until Actions is activated once for the fork (first human step below).
- `origin/main`, `upstream/main`, and local `HEAD` are all at the same commit
  (`f7e1e96`), so a dispatch runs exactly the checked-out code. Uncommitted local changes
  never affect CI; they run only in local commands.
- `gh` is authenticated as `nicolas-found42` with `repo` + `workflow` scopes, which cover
  workflow dispatch and run observation. No default-repo pin is set (`gh repo
  set-default nicolas-found42/nbadb`, per `docs/agents/issue-tracker.md`) — pass `-R` or
  set the pin before plain `gh` commands.
- **No repository secrets are configured yet.**

## Human-only prerequisites

1. **Activate Actions for the fork** — visit the GitHub Actions tab in a browser and
   accept the enable prompt. Until then the API registers no workflows and dispatch
   fails.
2. **NordVPN subscription + credentials** — from the Nord account dashboard's
   "manual setup" surface, obtain either the OpenVPN service credentials (username +
   password) or an access token. See the provider contract below for why no other
   provider works.
3. **Set repository secrets** on the fork (next section).
4. Optional, deferred until publication: `GH_TOKEN` (actions read + deployments write)
   and Kaggle credentials. Publication is decoupled from extraction; the terminal
   assurance scan does not need them.

## VPN provider contract: NordVPN only

The tunnel machinery is hard-coupled to NordVPN in three independent places:

- Server hostnames are validated against `^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.nordvpn\.com$`
  (`.github/actions/nordvpn-connect/connect.py:33-35`); anything else is rejected as
  `vpn_network_error`.
- Server selection consumes Nord's ranked recommendations, with fresh recommendations
  hash-partitioned across live slots and Nord's rank as tie-breaker (`AGENTS.md` >
  Full Extraction Control Plane; `.github/actions/nordvpn-connect/action.yml`
  `preferred-servers-json` / `quarantined-servers-json` inputs).
- Connectivity is OpenVPN only — `openvpn_udp` preferred, `openvpn_tcp` fallback
  (`action.yml` `technology` / `fallback-technology` inputs, defaults).

There is no WireGuard path anywhere in the tree (repo-wide search, 2026-09-19).

**Mullvad verdict: unusable, for two independent reasons.**
1. Mullvad cannot satisfy the Nord contract: an account number produces neither NordVPN
   service credentials nor `*.nordvpn.com` hostnames.
2. Mullvad removed OpenVPN support entirely on 2026-01-15 and is WireGuard-only
   (mullvad.net blog, "Removing OpenVPN 15th January 2026") — so even a hypothetical
   generic-OpenVPN adapter would have nothing to connect to.

Supporting Nord-only framing also appears in diagnostics redaction
(`src/nbadb/contracts/raw_request_authority.py:146-148`).

## Credential modes and secrets

Credential admission (`full-extraction.yml:2008-2024`) runs whenever
`network_mode != 'direct'`: either both `OPENVPN_USER` + `OPENVPN_PASSWORD`, or
`NORDVPN_TOKEN` — otherwise the run fails closed before any lane.

| Mode | Secrets | Concurrency | Cost |
| --- | --- | --- | --- |
| Configured credential | `OPENVPN_USER`, `OPENVPN_PASSWORD` (Nord service credentials) | `vpn_parallelism` lanes (input default `2`; production launches pass `6` and must pass the six-tunnel admission gate) | 6 of Nord's 10 simultaneous per-account connections |
| Token-derived | `NORDVPN_TOKEN` (access token; OpenVPN credentials derived at runtime via `api.nordvpn.com/v1/users/services/credentials` with a netrc file, `connect.py:842-848`) | At most one simultaneous matrix job; parallel recommendation partitioning disabled; capacity gate skipped | 1 connection |

Service credentials come from the Nord Account dashboard (`my.nordaccount.com` → NordVPN
→ Manual setup). Nord's docs are explicit that manual/third-party logins require these
service credentials, **not** the Nord Account email and password (support article
"Changes to the login process on third-party apps and routers"). Any plan includes
manual setup; a new subscription carries a 30-day money-back guarantee.

Robust setup: set **all three** secrets (`OPENVPN_USER`, `OPENVPN_PASSWORD`,
`NORDVPN_TOKEN`). Mode resolution is empirical, not presence-based: `vpn-auth-source`
is the preflight tunnel action's own output (`full-extraction.yml:1979`), so a valid
configured pair governs even when the token is also set. The connector prefers the
configured pair verbatim (`prepare_auth`, `connect.py:878-907`) and engages
token-derived service credentials only after an actual configured-credential rejection
(`switch_to_token_auth_after_rejection`, `connect.py:909-922`) — only then do the
parallel slot counts drop. Minimum viable is either the pair alone or the token alone.

Nord's connection rule (support article "How many devices can I use with NordVPN?"):
up to **10** simultaneous connections per account, and at most **5 per server**
(different protocols count separately on one server). The pipeline never shares a
server between live lanes (lane `N` owns preferred host `N`; fresh recommendations are
hash-partitioned across slots), so `vpn_parallelism=6` means 6 distinct servers with one
OpenVPN UDP connection each — inside both limits.

Upstream liveness, probed 2026-09-19 with the connector's own shapes: the
recommendations API returned `us8372.nordvpn.com` with `openvpn_udp`/`openvpn_tcp` for
the exact workflow query (country 228 + technology filter), and the `.ovpn` template
download (`downloads.nordcdn.com/configs/files/ovpn_udp/servers/<host>.udp.ovpn`,
`connect.py:1407-1410`) returned HTTP 200 with a valid OpenVPN config body. These
probes are freshness triggers: if dispatch fails in tunnel setup, re-probe both first.

## Dispatch surface

Key `workflow_dispatch` inputs (`full-extraction.yml:8-96`): `operation`
(`extract` / `continue` / `targeted_smoke`), `network_mode` (`vpn` / `auto` / `direct`),
`vpn_parallelism`, `direct_parallelism`, `direct_request_profile`,
`matrix_batch_size` (default 256), `chunk_profile`, `max_iterations` (default 64),
`retry_pipeline_failures` (default true). Continuation runs additionally require the
exact five-field source authority (`resume_source_run_id` + `resume_source_manifest`);
never inferred.

- **Without Nord credentials, `network_mode=direct` is the only runnable mode** (the
  credential check is skipped only for `direct`). Direct lanes use GitHub runners' own
  egress; the mode is supported and recent commits attest free/direct capacity, but
  NBA.com throttling/blocking of datacenter IPs is upstream-dependent — VPN is the
  canonical production path.
- `operation=targeted_smoke` is a one-lane **direct-only** exception, not a VPN path:
  the guard requires `network_mode=direct`, `vpn_parallelism=0`, `direct_parallelism=1`,
  exactly one lane and one iteration, forbids `retry_pipeline_failures`, and requires a
  manually supplied inline or artifact-backed lane manifest
  (`full-extraction.yml:297-300, 321-340`). It can never validate the VPN tunnel path.
  `AGENTS.md` still describes it as "one-lane VPN-only"; that wording is stale. It is
  never full-dataset assurance.
- **Mode-validation is a complete constraint set, not just credential admission**
  (`full-extraction.yml:277-292`, `workflow_guard` job): `network_mode` must be
  exactly `vpn`/`auto`/`direct`; `network_mode=vpn` requires `direct_parallelism=0`;
  `network_mode=direct` requires both `vpn_parallelism=0` and `direct_parallelism>=1`.
  Omitting `direct_parallelism` on a `vpn` dispatch leaves the workflow default (`2`)
  in place and fails `workflow_guard` with `network_mode=vpn requires
  direct_parallelism=0` before any lane runs (observed run `35428015854`,
  2026-09-19) — always pass it explicitly for `vpn`/`auto` dispatch.

```bash
gh workflow run full-extraction.yml -R nicolas-found42/nbadb --ref main \
  -f operation=extract -f network_mode=vpn -f vpn_parallelism=6 -f direct_parallelism=0
gh run watch -R nicolas-found42/nbadb <run-id>   # per iteration; the run self-chains
```

## Plan gate: support-matrix and adequacy-scorecard contract

The `plan` job runs `nbadb extract-completeness --require-full
--require-model-contract` and then two independent inline-Python gates over its
artifacts before `preflight`/`discovery_seed`/`vpn_capacity`/`extract` run
(`full-extraction.yml:466-563`). Both must pass; `preflight` is the first real Nord
credential test and only runs after they do.

1. **Support-matrix gap allowlist** (`full-extraction.yml:488-517`): fails if
   `gap_breakdown` (from `endpoint-support-summary.json`) contains any key other than
   `season_type_contract_blocked`. This is strictly stronger than `ci.yml`, which runs
   the same CLI without `--require-model-contract` and without this gate
   (`ci.yml:471-474`) — main can be green while `plan` is red.
2. **Adequacy scorecard** (`full-extraction.yml:526-563`): fails if
   `endpoint-adequacy-scorecard.json`'s summary has any nonzero
   `coverage_gap_endpoint_count`, `contract_gap_endpoint_count`,
   `downstream_unowned_endpoint_count`, or `downstream_excluded_endpoint_count`. This
   gate has **no allowlist at all** — it is driven by `contract_status`
   (`endpoint_coverage.py`'s per-row `"complete"` vs `"gap"`), so any nonempty
   `contract_gaps` list on a row keeps it counted here even if the specific gap key is
   allowlisted in gate 1. A fix must make the row's `contract_gaps` empty
   (`contract_status == "complete"`), not just relabel the gap key.

**Fixed 2026-09-19: `transform_contract_missing` misclassified authored
compatibility/reference endpoints.** Run `35428089035` failed gate 1 with
`{"transform_contract_missing": 8}` for `box_score_advanced_v2`,
`box_score_four_factors_v2`, `box_score_misc_v2`, `box_score_scoring_v2`,
`box_score_traditional_v2`, `box_score_usage_v2`, `league_standings_legacy`, and
`play_by_play_legacy`. All eight carry an explicit, maintainer-authored
`compatibility_reference_only` disposition in
`_MODEL_OWNERSHIP_STATS_ENDPOINTS` (`endpoint_coverage.py`) stating their staged data
is intentionally retained losslessly in silver with no star-schema consumer — the
same terminal disposition already used, without a gap, for the seven other
`compatibility_reference_only` endpoints that happen to have a transform (for
example `play_by_play_v2`), and already treated as a non-blocking field fate
(`sink_declared_reference_only`, `endpoint_coverage.py:2202-2206`) and as one of the
adequacy gate's own explicitly-classified passing buckets (its pass message
enumerates "compatibility-reference" endpoints alongside "modeled" and
"passthrough"). The endpoint-level gap logic
(`endpoint_coverage.py:2661-2674`, pre-fix) did not exempt this disposition from
`transform_contract_missing`, so structurally-absent transforms were misclassified as
a blocking contract gap instead of the terminal decision they actually are. Fix:
`compatibility_reference_only` rows no longer emit `transform_contract_missing` when
`transform_outputs` is empty; the disposition and its authored reason remain visible
on every row via the (unaffected) `downstream_status`/`downstream_reasons` fields, so
nothing is silently dropped per the repo's coverage trust floor. Verified:
`gap_breakdown` goes to `{}`, `contract_gap_endpoint_count` goes to `0`, and
`in_scope=142 extractable=139` is unchanged.

Local reproduction loop (no CI round trip needed for this class of bug):

```bash
uv run nbadb extract-completeness --require-full --require-model-contract \
  --output-dir /tmp/nbadb-coverage-local
jq -c '.gap_breakdown' /tmp/nbadb-coverage-local/endpoint-support-summary.json
jq '.summary.contract_gap_endpoint_count' \
  /tmp/nbadb-coverage-local/endpoint-adequacy-scorecard.json
```

The CLI's own exit code is not the pass/fail signal locally without
`--endpoint-analysis-docs-root` pointed at a pinned upstream `nba_api` checkout (it
exits 1 on a separate endpoint-analysis-docs check); assert on the two artifact
fields above, mirroring exactly what the two workflow gates read.

## Root cause: NBA Stats API fingerprint-blocks the Python `requests`/urllib3 client, not the VPN

**Diagnosed 2026-09-19, run chain `35430687683` → dedicated `Debug NBA Probe` workflow,
runs `35431455179`, `35431814071`, `35432038960`/`35432041682`, `35432609487`,
`35432932592`, `35433170984`.** `extract` was never reached: `preflight` legitimately
connects the OpenVPN tunnel and passes the lightweight curl-based control-plane and NBA
Stats probes, but the first real extractor call (`common_all_players`, via `nba_api`'s
`NBAStatsHTTP` → `requests.Session.get`) hangs for the full request timeout and fails
with `ConnectionError`/`RemoteDisconnected`/`ReadTimeout` on every attempt.

A same-VPN-session, interleaved A/B loop isolated the variable cleanly:

| Client | Endpoint | Result over 6 back-to-back rounds, same tunnel, same exit IP |
|---|---|---|
| `curl` (raw socket, curl's own TLS stack) | `commonteamyears` (control) | 6/6 success, ~0.1-0.2s each |
| `curl` | `commonallplayers` (target) | 6/6 success (single-call and paired runs), ~0.1-0.2s each |
| Python `requests.Session` replicating `nba_api`'s exact headers/params | `commonallplayers` | 6/6 `ReadTimeout`/`ConnectionError` at the timeout ceiling |

`curl` succeeded on the *identical* endpoint, over the *identical* tunnel and exit IP,
interleaved with (and immediately adjacent to) every `requests` failure. That rules out
VPN server quality, exit-IP reputation, DNS, per-endpoint throttling, and timing
correlation — the same IP is trusted for one client and dropped for the other on the
same request. NBA's edge is fingerprinting the TLS/HTTP client (JA3/ClientHello/HTTP-2
SETTINGS shape), not the network path. Because every one of the 162 registered
extractors calls through `nba_api.stats.library.http.NBAStatsHTTP`
(`requests.Session`-based), this blocks **all** VPN-routed extraction unconditionally —
it is not fixed by server rotation, capacity-gate tuning, or credential mode, all of
which the control plane already gets right.

**Not yet decided — needs a maintainer call, not a silent fix:** the remediation
requires replacing or wrapping the HTTP transport `nba_api` uses (e.g. a TLS/HTTP2
fingerprint-impersonating client such as `curl_cffi` swapped in for
`NBAStatsHTTP`'s session) without breaking the pinned `nba_api 1.11.4` contract,
`STATS_HEADERS` parity tests, or response parsing. This is a new runtime dependency and
a change to the exact request path every extractor and its tests assume. Full
primary-source evidence, ranked alternatives, and the maintainer decisions this requires
are gathered in [[../topics/tls-fingerprint-mitigation|TLS Fingerprint Mitigation for
the NBA Stats API]] — see open questions below.

## Root cause: a header permutation, not a VPN block — the empty-canary misdiagnosis

**Diagnosed 2026-09-19, run `35469167028`.** After the transport swap fixed the
fingerprint block above, `preflight` still failed. The canary reported
`failure_kind: "empty"` at `common_all_players` on eight consecutive NordVPN exits, each
one quarantined and rotated away by `f2ba74a`, until the server budget was exhausted and
the job failed closed. The apparent pattern — light `commonteamyears` probe passes,
heavier `commonallplayers` returns zero rows, every exit behaves identically — read as
NBA soft-blocking flagged exit IPs with success-shaped empty result sets.

**That reading was wrong.** The failure reproduces on a residential IP with no tunnel at
all, in about one second:

```
raw provider rows      : 582
extractor rows x width : 0 x 0
fallback reason_codes  : ('reordered_header',)
```

NBA returns `commonallplayers` headers in a different order depending on the request:
`TEAM_CODE` and `TEAM_SLUG` are transposed at indexes 12/13 under
`IsOnlyCurrentSeason=1` versus `=0`. Same sixteen columns, same names, two positions
swapped. `_strict_stats_packets` compared headers positionally, so the permuted response
was demoted to a lossless fallback, which reaches callers as a zero-width frame. The
probe read `height == 0` and called it empty.

The earlier "local proof" that the stack returned 5,224 rows was itself misleading: it
passed `params={...}` into `_sync_extract(extractor, **kwargs)`, so everything collapsed
into a single key named `params` and the call silently ran with defaults
(`is_only_current_season=0`, no season). 5,224 is the all-time player count. The probe's
real call was never exercised.

**Three consequences, all now fixed:**

- A pure permutation is admitted at the contract boundary. It carries the same closed
  column set under the same unique names, and downstream conversion addresses every
  column by name, so the wide frame is canonicalized to the pinned order while the
  receipt keeps the observed order. Anything other than a permutation still falls back.
- The probe reports `failure_kind=contract_drift` when a lossless fallback was produced,
  so drift can never again present as emptiness at that seam.
- `empty` is terminal again. It is host-independent evidence, so rotating servers on it
  burns the budget and hides a contract signal. Only transport exceptions rotate.

### Pinned contracts are stale against live NBA, and upstream cannot currently fix it

A sweep of the 24 endpoints callable without required IDs (2026-09-19, 36 live calls)
found nine drifting responses: one `reordered_header` (above) and eight
`additive_header`. NBA has added columns that the pinned contract does not carry:

| Endpoint | Added column(s) |
|---|---|
| `player_game_logs`, `player_game_logs_v2` | `NICKNAME`, `WNBA_FANTASY_PTS`, `FP_HIGH_SCORE`, `WNBA_FANTASY_PTS_RANK`, `FP_HIGH_SCORE_RANK`, `AVAILABLE_FLAG`, `MIN_SEC`, `TEAM_COUNT` |
| `all_time_leaders_grids` | `IS_ACTIVE_FLAG`, on all 19 result sets |
| `player_index` | `SUPPLEMENTAL_STATUS` |
| `draft_history` | `PLAYER_PROFILE_FLAG` |

These reached the runner as `lossless_drift`: raw bytes preserved, modeled wide table
empty. They do not block `preflight`, whose canary uses only `common_all_players` and
`league_game_log` — but they did block `discovery_seed` in run `35476517060`, because
`player_game_logs` is its primary player/team source and `player_index` is the designated
fallback, so both the primary and its backstop were zero-width.

**Upstream cannot supply these columns.** The pin is generated from nba_api's own docs
at the tag of the installed version, and `nba-api==1.11.4` is the latest release. Cloning
`v1.11.4` (HEAD `e0295f83`, matching the pinned SHA) shows the generator's authority,
`docs/nba_api/stats/endpoints/*.md`, documents none of these columns. `IS_ACTIVE_FLAG`
and `PLAYER_PROFILE_FLAG` appear only in `docs/nba_api/stats/endpoints_output/*.md`
sample tables, which the generator does not ingest; `SUPPLEMENTAL_STATUS` and the
`PlayerGameLogs` additions appear nowhere upstream. Bumping a version cannot fix this.

**Resolved with a dated local observation pin.** `src/nbadb/core/nba_api_observed_columns.py`
enumerates, per endpoint and result set, the columns NBA is observed to serve that
upstream does not document, and `_expected_result_sets` widens the generated contract by
exactly that delta. The pin is deliberately narrow:

- *Additive only.* It can never remove, rename or reorder a generated column.
- *Closed.* Anything beyond the generated pin plus the enumerated columns is still
  `additive_header`, still fatal.
- *Optional, not required.* NBA serves some admitted columns only for some requests:
  `PlayerGameLogs` returns `FP_HIGH_SCORE` and `FP_HIGH_SCORE_RANK` for the current
  season but not for historical ones, so only the admitted columns a given response
  actually carries are added. Pinning them as always-required turns an ordinary
  historical response into `removed_header`, which is how the first attempt failed.
- *Order-free.* Only names are pinned; the permutation tolerance above absorbs ordering.

**Freshness trigger: re-derive this table whenever `nba-api` is upgraded.** A release that
documents one of these columns makes its entry redundant, and a stale entry would mask a
genuine upstream removal. `admitted_result_set_columns` raises on a redundant entry, and
`test_every_admitted_entry_is_still_absent_from_the_generated_contract` fails when the
generated contract catches up.

After the pin, a re-run of the same 24-endpoint sweep reports zero drifting responses
across 36 calls, down from nine.

### What the remaining drift actually costs: completeness, not liveness

`extract` runs its lane matrix with `fail-fast: false`, and every downstream job
(`checkpoint`, `merge`, `dispatch_next`) is gated on `always() && !cancelled()` rather
than on `extract` succeeding. Lanes carry `failure_streak`, `class_failure_streak` and
`next_eligible_iteration`, and `dispatch_next` chains further iterations -- the plan for
run `35476517060` held 1,624 lanes across 7 planned waves with
`suggested_remaining_wave_count: 1119`.

That much is established. What is **not** established is whether a drifting endpoint can
halt the chain. `checkpoint`, `merge` and `dispatch_next` start on `always()` but their
`if:` also requires `needs.lane_control.result == 'success'`, and in run `35484551473`
`lane_control` failed and all three were skipped. So the chain can stop.

That run failed 256 of 256 lanes, so it cannot distinguish "lane_control demands every
lane green" from "lane_control tolerates partial failure and only this total failure
broke it" -- and its failure had a separate cause anyway (a missing CLI argument, below).
Until a run completes with *some* lanes failing and others succeeding, treat the blast
radius of endpoint drift as unknown rather than assuming it only costs completeness.

Note also that `publish` is hard-disabled (`if: ${{ false && ... }}`), so no chain
publishes until that is deliberately enabled.

### Two stacked workflow defects that blocked extract entirely

Neither of these was an extraction problem; both were workflow-definition bugs, and the
first hid the second.

**A truncated action SHA pin.** Every one of the 256 extract lanes in run `35484551473`
died in `Set up job`:

```
Unable to resolve action actions/download-artifact@3e5f45b2cfb9172054b408a40e8e0b5a5461e7c
```

That pin is 39 hex characters; a commit SHA is 40. The "Download exact current-run
raw-request authority" step had lost a single `7` from `...54b4087a40e8e...`. The other
nineteen `download-artifact` pins in the workflow already carried the correct SHA. An
audit of every `uses:` SHA across `.github/workflows` and `.github/actions` found this as
the only non-40-character pin, so a length check over that set is a cheap guard worth
keeping in mind.

**A missing required CLI argument in `lane_control`.** With the lanes failing fast,
`lane_control` ran for the first time and failed:

```
full_extraction_control.py resume: error: the following arguments are required:
--operation-authority-path
```

The `resume` subparser declares it required and the "Prepare next manifest" step never
passed it. `lane_control` runs on `always()` and gates `checkpoint`, `merge` and
`dispatch_next`, so this would have stopped the chain even with a fully green `extract`.
The plan job already uploads `operation-authority.json` beside `manifest.json` in the
artifact `lane_control` downloads, so the step now resolves it exactly as it already
resolves the manifest.

Worth noting for future diagnosis: reaching a new gate can expose a defect that was
previously unreachable rather than newly introduced. Both of these had been latent behind
`preflight`.

### Endpoint drift beyond discovery: the extract lanes

A second sweep covered the 101 registered endpoints that need IDs, which the first sweep
could not reach (fixtures: one player, one team, one game, season 2024-25). Result: 56
clean, 27 drifting, 18 error, 5 unreachable. **27 is an upper bound** -- `LeagueStandings`
was clean on a direct call, so some hits are parameter-sensitive rather than genuine.

Split by whether the additive-only observation pin can express them:

- **Pinnable, and now pinned.** `box_score_traditional_v2` (`NICKNAME`),
  `team_info_common`*, `common_player_info`*, `league_dash_lineups` and
  `team_dash_lineups` (`SUM_TIME_PLAYED`), `league_leaders` (`TEAM_ID`),
  `team_game_logs` (`AVAILABLE_FLAG`), `team_player_dashboard`, `league_lineup_viz`
  (`SUM_TM_MIN`), and both shot-location endpoints (`corner_3_fgm/fga/fg_pct`, plus
  `NICKNAME` on the player variant -- NBA added a "Corner 3" category).
- **Not expressible by a column-level pin.** `team_details` gained an entire new result
  set, `TeamAwardsCommCup` (the Emirates NBA Cup, introduced 2023-24); nothing was
  removed. Admitting a whole result set is a different mechanism from admitting columns
  within known ones.
- **Removals, 16 endpoints in waves 2-5.** `league_dash_team_stats` no longer sends
  `CFID`/`CFPARAMS`; `playoff_picture` dropped 35 COVID-era `ReturnToPlay_*` and
  `Seeding_Game_*` fields. A removal means the pinned contract requires a column the
  provider has stopped sending, which an additive-only pin cannot express by design.
  Deciding to admit a removal means accepting that a modeled column is simply gone, so it
  needs its own authority decision.

\* `team_info_common` and `common_player_info` are **not** pinned, despite being
pinnable. Both carry an older, separate defect: their pinned contracts sort a one-column
`AvailableSeasons` result set to canonical index 0, and `_from_nba_api` returns
`converted[0]`, so raw schema validation sees a one-column frame. Drift had been masking
this behind an empty frame; admitting their columns converts a silent empty into a hard
`ValidationError`, which is worse. The fix -- naming the wanted result set -- is small and
verified working locally (`team_info_common` returns 17 columns, `common_player_info` 34),
but it must edit `extract/stats/player_info.py` and `extract/stats/team_info.py`, both
frozen by the implicit-competition source authority
(`src/nbadb/contracts/nba_api_implicit_competition_current_source_v1_11_4.json`, 13 bound
files). Re-issuing that authority needs three independent derivation roots, an author role
and a predecessor receipt, so it is a governed action rather than a mechanical rebind.
Editing those files without re-issuing it fails 128 tests. Their pin entries were removed
so behaviour is unchanged rather than worse.

A measurement caveat worth keeping: the shot-location endpoints first looked unanalysable
because a naive header flatten produced duplicate `FGM`/`FGA` entries. Those endpoints use
two-level headers; the adapter's own `_fallback_headers` projects them to composite
snake_case names (`corner_3_fgm`). Diff against that projection, not against the raw
`headers` array.

### The two largest lane blocks are both broken, for different reasons

`video_details` and `video_details_asset` hold 156 lanes each -- 312 of the plan's 1,624,
about 19% -- and they sort first in the extract matrix, so they are the first real work
the chain attempts. Both fail as of 2026-09-19, and neither failure is contract drift.

**`video_details`: upstream returns no JSON.** Three consecutive direct calls
(`player_id=2544`, `team_id=1610612747`, season 2024-25, `context_measure=FGM`) returned
HTTP 500 with a body that is not JSON at all -- `JSONDecodeError: Expecting value: line 1
column 1`. Nothing on our side can pin around an empty body; this reads as NBA having
retired the endpoint. Decide whether to retire its lanes rather than retry them 156 times
per iteration.

**`video_details_asset`: the response is fine, our parser is not.** The same call returns
real data -- a 651-entry playlist -- but the extractor raises
`ResponseContractError: unknown response result occurrence name is malformed`.

Both endpoints are pinned with `parser_kind=legacy_result_sets` and an empty
`result_sets`, so their responses route to the unknown-response preservation path. That
handler expects the legacy list of named result sets and validates a `name` on each
entry, but the live response is a nested mapping:

```
resultSets = {"Meta": {"videoUrls": [...]}, "playlist": [...]}
```

`Meta` and `playlist` carry no `name`, so the occurrence-name check
(`nba_api_adapter.py:1808`) rejects the whole response. The adapter already implements a
`custom_nested` parser kind for exactly this shape -- these endpoints are simply pinned to
the wrong one. Because `parser_kind` comes from the generated contract, correcting it is
another contract-authority question rather than a local edit.

### Rebinding the star semantic corpora after any source change

Changing bound bytes under `src/nbadb/` invalidates the star semantic decision corpora,
which fail with `StarSemanticCorpusRebindError: current <label> authority drifted`. The
maintenance path is the module's own rebind contract
(`src/nbadb/contracts/rebind_star_semantic_decision_corpora.py`):

1. Re-derive the seven `_CURRENT_*_SHA256` pins by replaying `_compile_current_authorities()`
   (census, structural, candidate-source, stable, and the `dim_season_phase` candidate,
   disposition-semantic and authority digests) and update them in place.
2. Run `write_rebound_star_semantic_decision_corpora()` to regenerate both corpus JSONs.
3. Re-run `tests/unit/contracts/test_star_semantic_review_packet.py` and
   `test_rebind_star_semantic_decision_corpora.py` before committing. They prove two
   fresh rebinds are byte-identical, so a re-run after an accidental source change must
   reproduce the same bytes.

Not every pin moves. The adapter fix above moved five of seven; the structural and
season-phase candidate digests were unchanged.

## Terminal gate: MODEL-GREEN is unreachable by authoring (2026-09-20)

Every extract lane now reaches the runner and dies in the same place. `raw_request_assurance.py:311`
refuses to compile the raw-request authority unless `generation.model_green` is true:

```
RawRequestAssuranceError: raw-request assurance generation is not exact MODEL-GREEN evidence
```

Both completed lanes of run `35487068911` report GitHub `success` while carrying
`status: pipeline_failure`, `raw_status: extract-error`, `extract_exit_code: 1`,
`rows_persisted: 0`. The lane is not failing to reach the provider; it never starts.

### `model_green` is false unconditionally

`_model_blockers` (`src/nbadb/contracts/assurance.py:1878-2040`) ends with an unconditional
`blockers.extend([...])` that appends `independent_local_test_receipt_not_bound` and
`independent_review_receipt_not_bound`. An AST walk confirms zero enclosing conditionals: the
statement is at function-body level. `model_green = not blockers and deterministic_status == "GREEN"`
(`assurance.py:2453`). Those two rows are always present, so `model_green` is always `False`,
for every possible input to the generator. The gate cannot open on a locally generated assurance
no matter what is authored.

### Occurrences are not review decisions

The manifest's 141,681 is an occurrence count over 47 codes. The distinct subjects behind it:

| Authority child | Distinct subjects | Codes | Occurrences |
|---|---|---:|---:|
| `field-fate-contract.json` | 11,323 provider fields, 1,445 storage-only sinks, 6 zero-field routes | 11 | 71,544 |
| `metric-use-case-contract.json` | 4,337 public numeric columns | 15 | 64,677 |
| `star-table-contract.json` | 261 public tables, 420 FK relations | 14 | 3,369 |
| `stable-model-disposition.json` | 1,128 model candidates | 1 | 1,128 |
| `star-semantic-inventory.json` | 261 public tables | 3 | 523 |
| `temporal-availability-contract.json` | 438 route scopes | 1 | 438 |
| `not-generated` | 2 generation-level receipts | 2 | 2 |

### Three classes of blocker

**A. No admission seam exists — 139,928 occurrences (98.8%).** Four compilers take no arguments and
hardcode the unreviewed state:

- `compile_field_fate_contracts()` (`field_fate_contract.py:1086`) takes none; `_compile_field`
  (`:561`) writes `reviewed=False, green=False` and the four per-field codes as literals. The six
  `non_green_*` codes are derived name-match evidence from `_non_green_lineage_evidence`.
- `metric_use_case_registry()` (`metric_use_case_contract.py:756`) takes none, and `_validate_metric`
  (`:594`) *raises* if any non-formula semantic field is `reviewed` — "metric registry invented
  reviewed computed semantics". The contract asserts the blockers as an invariant, so authoring a
  metric review would make validation fail, not pass.
- `compile_star_table_contracts()` (`star_table_contract.py:821`) takes none; blockers are appended
  unconditionally at `:743-759`.
- `TemporalState = Literal["contract_blocked"]` (`temporal_availability_contract.py:36`) is the only
  inhabitable state, and the bundle compiler consumes no observations.

These are a census of a mechanism that has not been built, not a backlog. Writing the reviews would
change nothing, because there is nowhere to put them.

**B. A seam exists but is wired to empty — 1,651 occurrences.** `assurance.py:944-962` calls the two
authoring-capable compilers with literal empty tuples:

```python
stable_model_disposition = compile_stable_model_disposition_inventory(..., review_receipts=())
star_semantic_inventory = compile_star_semantic_inventory(
    ..., semantic_contracts=(), review_receipts=()
)
```

`src/nbadb/contracts/data/star-semantic-decisions-v1.json` is an authored corpus that exists in the
repository and is read only by `rebind_star_semantic_decision_corpora.py`. The assurance generator
never loads it, so the one authored decision does not reach the manifest.

**C. Structurally requires a second party — 1,130 occurrences.** All 1,128 dispositions are already
drafted by `draft_required_model_dispositions` (`stable_model_disposition.py:790`), each naming a
deterministic `pending_independent_model_disposition_review` digest. Its docstring is explicit: the
drafts are "deliberately not review evidence" and point at "a deterministic absent-review identity so
the disposition join stays red until a real independent receipt replaces it." `ReviewReceiptV1`
requires an `IndependenceEvidenceKind` — `independent_agent_review`, `maintainer_review`,
`protected_environment_approval` or `qualified_external_review`. The author of a decision cannot
supply its receipt. The two `not-generated` rows are the same requirement at generation scope.

### The precedent is one table

`star-semantic-decisions-v1.json` records `denominator_count: 261`, `decisions: 1`,
`unreviewed_table_ids: 260`; the dimensions shard records 18 and 1. The single worked example is
`dim_season_phase`, a three-column literal lookup — the simplest table in the warehouse. It still
carries one functional dependency, one key group, three lineage edges, three witness digests, purpose
/ row / temporal policies and six policy selections, each with its own `evidence_sha256`.

### Two circularities

`physical_field_capture_unobserved` (11,323) requires observed physical fields, and
`availability_unknown_pending_reviewed_evidence` (438) requires observed season intervals — all 438
scopes are `availability_state: unknown`, `planner_start_basis: fallback_attempt_unverified`. Both
are observations of extracted data, and extraction is what the gate blocks.

### The gate may be miscited

`nbadb contract-assurance` documents itself as a "MODEL diagnostic, not a DATA gate", and states that
"no workflow may treat this command's exit status as publication DATA authority"
(`src/nbadb/cli/commands/contract_assurance.py`). `raw_request_assurance.py:311` nevertheless makes
`model_green` a hard precondition for every extract lane. Whether extract should require MODEL-GREEN
at all is an open design question; it is not answered here and nothing was changed.

### Ordered path, cheapest first

1. Decide whether extract must require MODEL-GREEN. Cheapest by far if the answer is no.
2. Wire the existing seam: load the decision corpora in the generator and produce review receipts.
   Clears at most 1,651 occurrences and still needs an independent reviewer.
3. Build admission seams for field-fate, metric-use-case, star-table and temporal-availability. Four
   compilers need review inputs threaded through, and their validators relaxed from asserting
   *unreviewed* to accepting *reviewed*. Design and implementation work before any authoring can start.
4. Only then author: 11,323 fields, 4,337 columns, 261 tables twice over, 420 FK relations, 438 route
   scopes, 1,128 candidates — against a single worked example.
5. Resolve the two observation circularities, which need data this gate currently prevents collecting.

### Reproducing this locally

```bash
uv run nbadb contract-assurance --endpoint-analysis-docs-root <nba_api clone at v1.11.4>
```

Roughly two minutes, no network. It prints `MODEL-GREEN: RED` and all 47 blocker rows. The local run
of 2026-09-20 produced a blocker set identical to run `35487068911`'s manifest; only the generation
semantic digest differs, because it binds the source commit.

## Related notes

- [[../topics/full-extraction-control-plane|Full Extraction Control Plane]] — what the
  machine does once admitted
- [[run-modes|Run Modes]] — the local CLI equivalent (`init` / `daily` / `monthly` /
  `backfill run`)
- [[kaggle-distribution|Kaggle Distribution]] — the publication lane and its deferred
  credentials
- [[../topics/database-conventions|Database Conventions]] — what a completed build
  produces locally
- [[../topics/tls-fingerprint-mitigation|TLS Fingerprint Mitigation for the NBA Stats
  API]] — evidence base and ranked options for the open root-cause decision above

## Provenance

| Claim or section | Raw or canonical material | Notes |
|------------------|---------------------------|-------|
| dispatch inputs, credential admission, `targeted_smoke` guard | `.github/workflows/full-extraction.yml:8-96, 297-300, 321-340, 2008-2024` | line-anchored, read 2026-09-19; smoke guard supersedes stale `AGENTS.md` wording |
| configured-credential preference and token fallback on rejection | `.github/actions/nordvpn-connect/connect.py:878-907, 909-922` | `prepare_auth`, `switch_to_token_auth_after_rejection`; empirical mode via `full-extraction.yml:1979` |
| hostname allowlist and OpenVPN technologies | `.github/actions/nordvpn-connect/connect.py:32-35`, `action.yml` | Nord-only coupling |
| recommendation-driven server selection, capacity gate, token-derived serialization | `AGENTS.md` > Full Extraction Control Plane | maintainer contract |
| Mullvad OpenVPN removal 2026-01-15 | https://mullvad.net/en/blog/removing-openvpn-15th-january-2026 | primary source, stable historical event |
| NordVPN 10 simultaneous / 5 per-server rule | https://support.nordvpn.com/hc/en-us/articles/19476515228305-How-many-devices-can-I-use-with-NordVPN | volatile upstream fact; recheck before relying on >6 |
| service credentials (not account password) for manual setup | https://support.nordvpn.com/hc/en-us/articles/19685514639633-Changes-to-the-login-process-on-third-party-apps-and-routers | volatile upstream fact |
| 30-day money-back guarantee for new subscriptions | https://support.nordvpn.com/hc/en-us/articles/19476991311121-What-is-your-refund-policy | volatile upstream fact |
| upstream liveness probes (recommendations API, `.ovpn` download) | `api.nordvpn.com`, `downloads.nordcdn.com`, probed 2026-09-19 with connector's exact query/URL shapes | dated runtime observation; freshness trigger |
| no WireGuard support in tree | repo-wide grep for `wireguard`, 2026-09-19 | absence observation |
| fork state (visibility, Actions enablement, zero registered workflows, no secrets, HEAD parity) | GitHub REST API + local `git`, observed 2026-09-19 | dated runtime observation; freshness trigger for this note |
| mode-validation constraint set and `direct_parallelism=0` requirement | `.github/workflows/full-extraction.yml:277-292`; observed run `35428015854`, 2026-09-19 | line-anchored, read 2026-09-19 |
| plan-gate two-gate contract (support-matrix allowlist, adequacy scorecard) | `.github/workflows/full-extraction.yml:466-563`, `ci.yml:471-474` | line-anchored, read 2026-09-19 |
| `transform_contract_missing` misclassification and fix | `src/nbadb/core/endpoint_coverage.py` (`_MODEL_OWNERSHIP_STATS_ENDPOINTS`, gap logic ~2202-2206, ~2661-2674); run `35428089035`, 2026-09-19 | fixed same day; local repro verified `gap_breakdown={}`, `contract_gap_endpoint_count=0` |
| `requests`/urllib3 TLS-fingerprint block vs curl; interleaved A/B isolation | Dedicated `Debug NBA Probe` workflow, runs `35431455179`, `35431814071`, `35432038960`, `35432041682`, `35432609487`, `35432932592`, `35433170984`, 2026-09-19; `nba_api/stats/library/http.py:31-58` (exact client path) | dated runtime observation; diagnostic scripts deleted after use, evidence retained here |
| header permutation root cause; `reordered_header` -> lossless fallback -> zero-width frame | `src/nbadb/extract/nba_api_adapter.py` (`_strict_stats_packets`, `_header_anomalies`), `src/nbadb/extract/base.py:1053`; run `35469167028` preflight log; local repro 2026-09-19 | dated runtime observation; repro is residential-IP, no tunnel, ~1s |
| `commonallplayers` TEAM_CODE/TEAM_SLUG transposition under `IsOnlyCurrentSeason=1` | live `nba_api` calls, both flag values, 2026-09-19 | dated runtime observation; volatile provider behaviour |
| eight exits quarantined then budget exhausted | run `35469167028`, `FAILED_SERVERS_JSON` in preflight job log | line-anchored to run log |
| endpoint drift sweep: 24 endpoints, 36 calls, 9 drifting | live sweep 2026-09-19, results in session scratch | dated runtime observation; rerun to refresh |
| upstream docs lack the added columns at `v1.11.4` | `swar/nba_api` clone at tag `v1.11.4`, HEAD `e0295f83`, `docs/nba_api/stats/endpoints/` vs `endpoints_output/`, read 2026-09-19 | matches `NBA_API_UPSTREAM_COMMIT`; freshness trigger on any nba-api bump |
| corpus rebind procedure and which pins move | `src/nbadb/contracts/rebind_star_semantic_decision_corpora.py` docstring and `_compile_current_authorities`; applied 2026-09-19 | maintainer contract; verified by the two rebind test files |
| local observation pin for undocumented provider columns | `src/nbadb/core/nba_api_observed_columns.py`; live header diffs against `pinned_endpoint_contract(...)`, 2026-09-19 | dated runtime observation; freshness trigger on any `nba-api` upgrade, guarded by a test |
| `FP_HIGH_SCORE`/`FP_HIGH_SCORE_RANK` are current-season-only on `PlayerGameLogs` | live calls for 2005-06, 2015-16, 2024-25, 2025-26, 2026-09-19 | dated runtime observation; motivates optional-not-required admission |
| `discovery_seed` depends on `player_game_logs` and falls back to `player_index` | `src/nbadb/orchestrate/discovery.py:1399, 1240`; run `35476517060` job log | line-anchored, read 2026-09-19 |
| post-pin sweep: 36 calls, zero drift | live sweep 2026-09-19 after the pin | dated runtime observation; rerun to refresh |
| extract lanes tolerate lane failure; downstream jobs run on `always()` | `.github/workflows/full-extraction.yml:3088-3091` (`fail-fast: false`), job `if:` guards for `checkpoint`/`merge`/`dispatch_next`; lane manifest of run `35476517060` (1,624 lanes, 7 waves) | line-anchored, read 2026-09-19 |
| ID-requiring endpoint sweep: 101 attempted, 27 drifting (upper bound) | live sweep 2026-09-19 with one player/team/game fixture, season 2024-25 | dated runtime observation; parameter-sensitive hits inflate the count |
| `team_details` gained the `TeamAwardsCommCup` result set | live call vs `pinned_endpoint_contract(TeamDetails)`, 2026-09-19 | dated runtime observation; additive_result_set, not a column change |
| `league_dash_team_stats` lost `CFID`/`CFPARAMS`; `playoff_picture` lost 35 COVID-era fields | live calls vs pinned contracts, 2026-09-19 | dated runtime observation; genuine provider removals |
| shot-location endpoints need the `_fallback_headers` composite projection | `src/nbadb/extract/nba_api_adapter.py` (`_fallback_headers`), two-level `headers` objects observed 2026-09-19 | method note; a naive flatten yields duplicate FGM/FGA and is wrong |
| `player_info.py`/`team_info.py` are frozen by the implicit-competition source authority | `src/nbadb/contracts/nba_api_implicit_competition_current_source_v1_11_4.json` (13 `source_bindings`); `implicit_competition_source_authority.py` writer requires three independent roots | governed artifact; editing a bound file fails 128 tests |
| `publish` is hard-disabled | `.github/workflows/full-extraction.yml:5441` (`if: ${{ false && ... }}`) | line-anchored, read 2026-09-19 |
| truncated `download-artifact` pin killed all 256 extract lanes | run `35484551473` extract job logs (`Set up job`); `.github/workflows/full-extraction.yml` pin audit, 2026-09-19 | fixed in `a3d2cc5`; all twenty pins now identical |
| `lane_control` resume missing `--operation-authority-path` | run `35484551473` lane_control log; `src/nbadb/orchestrate/full_extraction_control.py:9764` (`required=True`) | fixed in `53b6f2e`; line-anchored |
| `checkpoint`/`merge`/`dispatch_next` skip when `lane_control` fails | run `35484551473` job outcomes; their `if:` requires `needs.lane_control.result == 'success'` | dated runtime observation; blast radius of partial lane failure still unknown |
| `video_details` returns non-JSON behind HTTP 500 | three direct `nba_api` calls, 2026-09-19 | dated runtime observation; persistent, not transient |
| `video_details_asset` returns a nested `resultSets` mapping our unknown-response path rejects | direct call (651-entry playlist) vs `src/nbadb/extract/nba_api_adapter.py:1808`; `parser_kind=legacy_result_sets`, `result_sets=[]` | dated runtime observation; `custom_nested` already exists for this shape |
| the two video endpoints are 312 of 1,624 lanes and sort first in the matrix | lane manifest of run `35476517060` | derived from the manifest; recheck after any replan |
| MODEL-GREEN blocks every extract lane | run `35487068911`, jobs `106017368499` and `106017858630`; `extraction-lane-metadata-...` (`status: pipeline_failure`, `extract_exit_code: 1`, `rows_persisted: 0`); `src/nbadb/orchestrate/raw_request_assurance.py:311` | line-anchored, read 2026-09-20; both completed lanes identical |
| `model_green` is unconditionally false | `src/nbadb/contracts/assurance.py:1878-2040` (`_model_blockers`, unconditional trailing `blockers.extend`) and `:2453` (`model_green = not blockers and ...`); AST walk shows no enclosing conditional | static proof, 2026-09-20; holds for every generator input |
| 141,681 occurrences decompose to far fewer subjects | `assurance-manifest.json` `model_blockers` plus entity counts from `stable-model-disposition.json`, `temporal-availability-contract.json`, `star-semantic-decisions-v1.json` of run `35487068911` | derived from the generated children; recheck after any authority change |
| four authorities have no admission seam | `field_fate_contract.py:561, 1086`; `metric_use_case_contract.py:594, 756`; `star_table_contract.py:743-759, 821`; `temporal_availability_contract.py:36` | line-anchored, read 2026-09-20; `_validate_metric` rejects reviewed fields outright |
| the two authoring-capable compilers are wired to empty tuples | `src/nbadb/contracts/assurance.py:944-962` | line-anchored, read 2026-09-20 |
| the authored decision corpus never reaches the generator | `src/nbadb/contracts/data/star-semantic-decisions-v1.json`; sole importer is `rebind_star_semantic_decision_corpora.py` | repository-wide grep, 2026-09-20 |
| 1,128 dispositions are drafted; only independent receipts are missing | `stable-model-disposition.json` (`dispositions: 1128`, `review_receipts: 0`); `stable_model_disposition.py:790` docstring; `review_evidence.py` `IndependenceEvidenceKind` | line-anchored; fail-closed by design, not a defect |
| one of 261 star tables is authored | `star-semantic-decisions-v1.json` (`denominator_count: 261`, `decisions: 1`); dimensions shard 18/1 | counted 2026-09-20; the worked example is `dim_season_phase` |
| MODEL-GREEN is documented as a diagnostic, not a gate | `src/nbadb/cli/commands/contract_assurance.py` docstring vs `raw_request_assurance.py:311` | open design question; nothing changed |
| local assurance reproduces the CI blocker set exactly | `uv run nbadb contract-assurance --endpoint-analysis-docs-root <v1.11.4 clone>`, 2026-09-20, vs run `35487068911` manifest | ~2 min, no network; only the generation semantic digest differs |
