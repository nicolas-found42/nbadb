---
title: TLS Fingerprint Mitigation for the NBA Stats API
tags:
  - kb
  - topics
  - extraction
  - http
  - nba-api
aliases:
  - curl_cffi Migration Research
  - NBA Stats Client Fingerprint Block
kind: concept
status: active
updated: 2026-09-19
source_count: 14
---

# TLS Fingerprint Mitigation for the NBA Stats API

Decision-support note for the block diagnosed in
[[../operations/full-extraction-requirements#Root cause: NBA Stats API fingerprint-blocks the Python `requests`/urllib3 client, not the VPN|Full Extraction Requirements § Root cause]]:
NBA's edge fingerprints the TLS/HTTP-2 client shape, not the request path or IP, so
Python `requests` (every one of nbadb's 162 extractors, via `nba_api`'s `NBAStatsHTTP`)
times out while `curl` on the identical tunnel/exit IP/endpoint succeeds every time.
**Remediation is implemented (2026-09-19)**: nbadb's own session factory now returns a
`curl_cffi` session; see "Implemented remediation" below. The research sections that
follow are retained as the evidence base, researched 2026-09-19 against primary sources
only (official docs/source, GitHub issue/PR bodies, PyPI/GitHub API metadata). Full
session output: `artifact://356` (`/tmp/nbadb-research-tls-fingerprint-mitigation.md`,
superseded by this note as the maintained record).

## Implemented remediation (2026-09-19)

`src/nbadb/extract/nba_api_adapter.py` replaces the `requests.Session` +
`HTTPAdapter` construction with:

- `_PinnedTransportSession(curl_cffi.requests.Session)` — `impersonate="chrome"`,
  `default_headers=False`, `retry=0`, `verify=certifi.where()` (see decisions below for
  each choice), plus a `request()` override that projects provider query parameters
  onto `requests`' exact wire semantics (`_requests_compatible_params`: `None` values
  omitted, `bool` via `str()` — `curl_cffi` would otherwise emit the literal `"None"`
  / JSON `true`/`false`) and enforces the no-ambient-proxy contract in code.
- Per-thread session identity is unchanged (`_ThreadLocalSessionMixin` + `evict_session`).
- `certifi` is now a direct dependency in `pyproject.toml` (previously transitive).

The ambient-proxy point deserves emphasis: `curl_cffi` 0.16.3 accepts `trust_env` but
never reads it, so the old `trust_env=False` contract was silently lost in the swap.
The adapter now neutralizes it per call (`proxies={"all": ""}` when neither the call nor
the session carries an explicit proxy — libcurl's documented opt-out from the
`http_proxy`/`https_proxy`/`ALL_PROXY` env lookup), and
`tests/unit/extract/test_nba_api_adapter.py::test_provider_sessions_are_thread_local_and_ignore_ambient_proxies`
asserts both halves (empty-string opt-out injected, explicit proxy preserved). Failure
classification was extended in kind: `nbadb.core.extraction_failures` recognizes
libcurl transport-layer error names (`ConnectError`, `ReadError`, `ProtocolError`,
HTTP/2 stream-fault codes, …) as `transport_transient` so the existing bounded-retry
routing treats curl-transport faults exactly like the `requests` faults they replace.

## Why the block is client-identity, not network (evidence chain)

- **Akamai's own white paper** (Segal/Fridman/Shuster 2017) defines the HTTP/2
  fingerprint format from SETTINGS/WINDOW_UPDATE/PRIORITY frame shape and pseudo-header
  order, and shows curl's shape already differs from Chrome's — the mechanism NBA's edge
  (Akamai-fronted) can key on.
- **Cloudflare's docs** confirm JA3/JA4 TLS fingerprints are a documented
  Enterprise Bot-Management signal ("may be useful in blocking an incoming threat") and
  that header-order mismatches are a separate detection signal — but do **not** document
  HTTP/2-frame fingerprinting, so this is Akamai/first-party territory, consistent with
  `stats.nba.com`.
- **JA3/JA4 specs**: JA3 hashes ClientHello version/ciphers/extensions/curves/formats;
  Python's `ssl` module (what `requests`/urllib3 use) cannot reorder or omit these —
  there is no API surface for it — so a `requests` ClientHello is structurally
  OpenSSL-shaped and cannot match a browser's, independent of headers or IP.
- **nbadb's own interleaved A/B test** (`full-extraction-requirements.md`'s Root Cause
  section) reproduced this live: 6/6 `curl` passes vs 6/6 Python `requests` failures,
  same tunnel/IP/endpoint, ruling out VPN/IP/DNS/throttling as the variable.
- **`swar/nba_api` issue tracker corroborates the same client-differential going back to
  2019** (`#30`, `#155`) and again in 2026 (`#652`, opened 2026-03-12, still open):
  plourr03 diagnosed "NBA tightened their Bot Manager. It now also checks the TLS
  fingerprint of the request, not just cookies" and posted the only tracker workaround —
  a `curl_cffi` session monkeypatched onto `NBAStatsHTTP.get_session` — with one
  corroborating report and one counter-report (endpoint- and profile-dependent). The
  pinned `nba_api==1.11.4` header fix (`#633`/`#636`, released 2026-02-20) only updated
  the User-Agent; later reports (`#652`, `#691` as recently as 2026-09-09) say headers
  alone stopped being sufficient after a further Bot Manager tightening — consistent with
  nbadb hitting the block on the pinned, header-correct release.

## `nba_api` 1.11.4's extension point — and why nbadb bypasses it

`nba_api/library/http.py` (installed source sha256-verified identical to tag `v1.11.4`)
ships a first-party, test-covered session-injection seam: `NBAHTTP._session` /
`get_session()` / `set_session()` (lines 67-79), added via feature request `#485` and PR
`#486` (merged 2025-01-11) specifically so callers can swap the global session without
forking 200+ endpoint files. This is the seam the tracker's blocking workarounds
actually use (`#652` monkeypatches `get_session`; `#633` resets `_session` to drop stale
connections).

**nbadb does not go through it.** `src/nbadb/extract/nba_api_adapter.py` defines its own
`_ThreadLocalSessionMixin.get_session` (lines 860-897, thread-local, now returning the
`_PinnedTransportSession` described above) and
`NbaDbStatsHTTP(_ThreadLocalSessionMixin, NBAStatsHTTP)` (line 898) — nbadb's mixin
wins the MRO over `NBAHTTP.get_session`. Calling `NBAStatsHTTP.set_session(...)` alone
would therefore be a silent no-op for nbadb; **the effective seam is nbadb's own mixin**,
not `nba_api`'s documented hook.

## Ranked alternatives

| Rank | Option | Verdict |
|---|---|---|
| 1 | **`curl_cffi` direct session swap** | fewest moving parts, first-party maintained, exact API fit, one new dependency |
| 2 | `curl-adapter` (`session.mount(..., CurlCffiAdapter(...))`) | keeps the `requests.Session` object/tests untouched; costs a second dependency+native stack for the same underlying engine |
| 3 | `tls-client` (Python bindings for Go `utls`) | capable (custom JA3 + H2), but the Python binding is ~2 years stale and needs a `proxies=`/`timeout=`-name translation shim |
| 4 | `impit` / `primp` / `wreq` | actively maintained, capable, but each needs an adapter from a non-`requests` API; no advantage over `curl_cffi` here |
| 5 | `curl-impersonate` CLI / `pycurl`+libcurl-impersonate | correct engine, wrong shape (subprocess-per-request or build/link complexity); useful only as a verification probe |
| 6 | `httpx` (even with `http2=True`) | **not viable** — Python's `ssl` module cannot reorder/shape the ClientHello; httpx would only present a different non-browser fingerprint |

Renames/dead ends: `rnet` → superseded by `wreq`; `tls_requests` is not a real PyPI
name (the actual package is `wrapper-tls-requests`, itself a facade over the stale
`tls-client` binding); `hrequests` is stale (last release 2024-12-01).

## Decisions taken (was: "Decisions for the maintainer")

1. **`default_headers=False` vs. letting `curl_cffi` merge browser defaults.** nbadb's
   pinned `STATS_HEADERS` already look like a browser XHR call; merging navigation-style
   defaults (`Sec-Fetch-Mode: navigate`, `Upgrade-Insecure-Requests`, …) creates a mixed
   signal and changes header order. **Taken as recommended**: `default_headers=False`.
2. **Impersonation profile.** **Deviation from the earlier recommendation, deliberate:**
   implemented with the versionless `impersonate="chrome"`, not `chrome145`. The
   versionless alias is only "drifty" under floating dependencies; this repo pins
   `curl_cffi==0.16.3` exactly, so the alias resolves to one fixed profile per
   lockfile, and any dependency bump is already a deliberate act that re-runs the
   probe contract. Empirical validation during the diagnosis (live probe through the
   tunnel) used `"chrome"` and passed, so the code matches the validated shape.
3. **HTTP/2 fallback knob.** If NBA's edge ever throws `curl_cffi`'s documented
   `ErrCode: 92` (broken h2 stream), the mitigation is `http_version=CurlHttpVersion.V1_1`
   — kept as an operator-level knob, not hardcoded. The transport-class classifier now
   recognizes the stream-fault code names as `transport_transient`, so a future knob
   activation slots into existing retry routing.
4. **Ambient proxy hygiene.** **Superseded by in-code enforcement**: instead of asking
   workflows not to export proxy vars, the session's `request()` injects
   `proxies={"all": ""}` whenever neither the call nor the session sets one, and the
   regression test proves ambient `HTTPS_PROXY` is ignored while explicit proxies stay
   authoritative. `trust_env=False` was dropped (inert in `curl_cffi`).
5. **`_ThreadLocalSessionMixin.evict_session()` and `HTTPAdapter` removal.** `curl_cffi`
   has no adapter/`mount()` concept — the `HTTPAdapter(pool_connections=1,
   pool_maxsize=1)` mount did not survive the swap; `Session.close()` in
   `evict_session` replaces the adapter-pool-size role. **Taken as expected.**
6. **CA trust anchors (new).** `requests` pinned verification to `certifi`; libcurl
   defaults to `ssl.get_default_verify_paths()` and honors ambient
   `SSL_CERT_FILE`/`CURL_CA_BUNDLE`/`REQUESTS_CA_BUNDLE`. The session pins
   `verify=certifi.where()` (and `certifi` became a direct dependency) so trust anchors
   are byte-identical to the pre-swap contract and environment-independent.

## Non-goals (explicit)

Do not fork `nba_api`; do not monkeypatch `nba_api.library.http.requests` at module
scope (affects every `requests` consumer in-process and is unnecessary since the session
factory is already nbadb-owned); do not change the pinned `STATS_HEADERS` (parity tests
pin it); do not use `NBAStatsHTTP.set_session` for nbadb itself (bypassed by the MRO
above), though it remains the correct hook for any other downstream consumer of
`nba_api` directly.

## Verification (completed 2026-09-19; live CI confirmation pending)

1. The interleaved A/B probe that diagnosed the block (curl vs `requests`, same
   tunnel/exit IP/endpoint) is recorded in
   [[../operations/full-extraction-requirements|Full Extraction Requirements]]; the
   transport swap was validated with the same client-differential logic — the swapped
   session reuses the validated browser-fingerprint shape.
2. `tests/unit/extract/` green (1195 passed): the session-identity test was replaced,
   not re-pinned — it now asserts thread-local identity, `verify == certifi.where()`,
   the injected `{"all": ""}` proxy opt-out, and preservation of an explicit proxy;
   it fails red against the pre-fix session (verified by reverting the injection).
3. Ambient-proxy smoke: with `HTTPS_PROXY` pointed at a dead port,
   `trust_env=False` on `curl_cffi` still routes through the proxy (connection
   failure) while nbadb's pinned session reaches the host — the leak the old test
   could not see.
4. Live confirmation against `stats.nba.com` through the CI VPN lane is the remaining
   open item; local runs cannot reach the edge from this network.

## Related notes

- [[../operations/full-extraction-requirements|Full Extraction Requirements]] — the
  operational note this decision blocks (`extract` stage of `full-extraction.yml`)
- [[extractor-surface|Extractor Surface]] — the extractor call path this seam sits under
- [[nba-api-source-summary|NBA API Source Summary]] — the broader `nba_api` dependency
  boundary

## Provenance

| Claim or section | Raw or canonical material | Notes |
|------------------|---------------------------|-------|
| root-cause chain, A/B evidence | `kb/wiki/operations/full-extraction-requirements.md` § Root cause | prior note this one extends |
| `nba_api` 1.11.4 session hook, sha256-verified against tag | `.venv/lib/python3.12/site-packages/nba_api/library/http.py:67-79`; `https://raw.githubusercontent.com/swar/nba_api/v1.11.4/...` | verified byte-identical 2026-09-19 |
| nbadb's own session seam and MRO bypass | `src/nbadb/extract/nba_api_adapter.py:809-838, 2207-2222` | line-anchored, read 2026-09-19 |
| session-injection feature request and merged design | `https://github.com/swar/nba_api/issues/485`, `https://github.com/swar/nba_api/pull/486` | rsforbes' review comment defines shipped `_session`/`get_session`/`set_session` |
| TLS-fingerprint diagnosis + `curl_cffi` workaround in the wild | `https://github.com/swar/nba_api/issues/652` (plourr03, 2026-05-13; counter-report samiaab1990, 2026-06-04) | single-user report + counter-report, evidence not proof |
| pinned header fix (v1.11.4) and its later insufficiency | `https://github.com/swar/nba_api/issues/633`, `.../pull/635`, release notes `v1.11.4` (2026-02-20); later reports `#652`, `#691` (2026-09-09) | official fix addressed UA only |
| cloud/VPN IP-block history and documented proxy escape hatch | `https://github.com/swar/nba_api/issues/176,#101,#30,#320,#498,#510`; `docs/nba_api/stats/examples.md` in upstream repo | maintainer (`swar`)/reviewer (`rsforbes`) statements |
| curl_cffi capability, maintenance, and API-contract fit | `https://api.github.com/repos/lexiforest/curl_cffi`, `https://pypi.org/pypi/curl_cffi/0.16.3/json`, `https://raw.githubusercontent.com/lexiforest/curl_cffi/main/README.md`, `curl_cffi/requests/session.py`, `curl_cffi/requests/impersonate.py` | v0.16.3, 2026-09-02; sources inspected at `main`, 2026-09-19 |
| curl-impersonate engine and browser-shape claim | `https://raw.githubusercontent.com/lexiforest/curl-impersonate/main/README.md`; `https://curl-impersonate.readthedocs.io/en/latest/fingerprints.html` | active fork, latest release v2.2.3, 2026-09-16 |
| Akamai HTTP/2 fingerprint mechanism | Akamai white paper "Passive Fingerprinting of HTTP/2 Clients" (2017), Wayback capture; `https://techdocs.akamai.com/application-security/reference/get-ja4-fingerprint-settings` | live PDF returns 403 to automation; used Wayback copy |
| Cloudflare JA3/JA4 documentation scope | `https://developers.cloudflare.com/bots/additional-configurations/ja3-ja4-fingerprint/`, `.../bots/concepts/bot-score/`, `.../bots/additional-configurations/detection-ids/` | confirms TLS/JA3-JA4 + header-order signals; no documented H2-frame fingerprinting |
| JA3/JA4 hash construction | `https://github.com/salesforce/ja3`, `https://github.com/FoxIO-LLC/ja4` | field order and sorting behavior |
| `requests`/urllib3 cannot shape ClientHello; HTTP/2 experimental | `https://urllib3.readthedocs.io/en/stable/changelog.html`; `https://www.python-httpx.org/http2/`, `.../advanced/ssl/` | rules out httpx as a fix |
| alternatives survey (`tls-client`, `impit`, `primp`, `wreq`, `pycurl`, `curl-adapter`) | `https://pypi.org/pypi/tls-client/json`, `https://api.github.com/repos/FlorianREGAZ/Python-Tls-Client`, `https://pypi.org/pypi/impit/json`, `https://pypi.org/pypi/primp/json`, `https://pypi.org/pypi/wreq/json`, `https://pypi.org/pypi/curl-adapter/json` | metadata dated 2026-09; ranked in table above |
