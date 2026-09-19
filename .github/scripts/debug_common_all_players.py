from __future__ import annotations

import time

import polars as pl

from nbadb.extract.stats.player_info import CommonAllPlayersExtractor
from nbadb.orchestrate.extractor_runner import _sync_extract
from nbadb.orchestrate.seasons import current_season


def _describe(label: str, season: str, timeout: int) -> None:
    print(f"--- {label}: season={season!r} timeout={timeout} ---", flush=True)
    started = time.monotonic()
    try:
        frame: pl.DataFrame = _sync_extract(
            CommonAllPlayersExtractor(),
            season=season,
            is_only_current_season=1,
            allow_static_fallback=False,
            timeout=timeout,
        )
    except Exception as exc:  # noqa: BLE001
        elapsed = time.monotonic() - started
        print(f"EXCEPTION after {elapsed:.1f}s: {type(exc).__name__}: {exc}", flush=True)
        return
    elapsed = time.monotonic() - started
    print(
        f"OK after {elapsed:.1f}s rows={frame.height} columns={sorted(frame.columns)}", flush=True
    )
    if frame.height == 0:
        print("EMPTY FRAME", flush=True)
        return
    positive = 0
    total = 0
    team_ids: set[int] = set()
    sample = []
    for row in frame.select("person_id", "team_id").iter_rows(named=True):
        total += 1
        try:
            player_id = int(row["person_id"])
            team_id = int(row["team_id"])
        except (TypeError, ValueError):
            continue
        team_ids.add(team_id)
        if len(sample) < 8:
            sample.append((player_id, team_id))
        if player_id > 0 and team_id > 0:
            positive += 1
    print(f"total_rows_checked={total} positive_player_team_rows={positive}", flush=True)
    print(
        f"distinct_team_ids_count={len(team_ids)} sample_team_ids={sorted(team_ids)[:10]}",
        flush=True,
    )
    print(f"sample_person_team_ids={sample}", flush=True)


def main() -> int:
    computed = current_season()
    print(f"current_season() -> {computed!r}", flush=True)
    _describe("hardcoded-default-60s", "2024-25", 60)
    _describe("dynamic-current-60s", computed, 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
