from __future__ import annotations

import os
import time

import polars as pl

from nbadb.extract.stats.player_info import CommonAllPlayersExtractor
from nbadb.orchestrate.extractor_runner import _sync_extract
from nbadb.orchestrate.seasons import current_season


def _attempt(season: str, timeout: int) -> pl.DataFrame:
    return _sync_extract(
        CommonAllPlayersExtractor(),
        season=season,
        is_only_current_season=1,
        allow_static_fallback=False,
        timeout=timeout,
    )


def _describe(season: str, timeout: int, attempts: int) -> None:
    print(f"--- season={season!r} timeout={timeout} max_attempts={attempts} ---", flush=True)
    frame: pl.DataFrame | None = None
    for attempt in range(1, attempts + 1):
        started = time.monotonic()
        try:
            frame = _attempt(season, timeout)
        except Exception as exc:  # noqa: BLE001
            elapsed = time.monotonic() - started
            print(
                f"attempt {attempt}/{attempts} EXCEPTION after {elapsed:.1f}s: "
                f"{type(exc).__name__}: {exc}",
                flush=True,
            )
            if attempt < attempts:
                time.sleep(5)
            continue
        elapsed = time.monotonic() - started
        print(f"attempt {attempt}/{attempts} OK after {elapsed:.1f}s", flush=True)
        break
    if frame is None:
        print("ALL ATTEMPTS FAILED", flush=True)
        return
    print(f"rows={frame.height} columns={sorted(frame.columns)}", flush=True)
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
    season = os.environ.get("DEBUG_SEASON") or "2024-25"
    _describe(season, timeout=90, attempts=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
