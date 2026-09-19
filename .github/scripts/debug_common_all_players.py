from __future__ import annotations

import polars as pl

from nbadb.extract.stats.player_info import CommonAllPlayersExtractor
from nbadb.orchestrate.extractor_runner import _sync_extract
from nbadb.orchestrate.seasons import current_season


def _describe(label: str, season: str) -> None:
    print(f"--- {label}: season={season!r} ---")
    try:
        frame: pl.DataFrame = _sync_extract(
            CommonAllPlayersExtractor(),
            season=season,
            is_only_current_season=1,
            allow_static_fallback=False,
            timeout=20,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"EXCEPTION: {type(exc).__name__}: {exc}")
        return
    print(f"rows={frame.height} columns={sorted(frame.columns)}")
    if frame.height == 0:
        print("EMPTY FRAME")
        return
    positive = 0
    total = 0
    sample = []
    for row in frame.select("person_id", "team_id").iter_rows(named=True):
        total += 1
        try:
            player_id = int(row["person_id"])
            team_id = int(row["team_id"])
        except (TypeError, ValueError):
            continue
        if len(sample) < 5:
            sample.append((player_id, team_id))
        if player_id > 0 and team_id > 0:
            positive += 1
    print(f"total_rows_checked={total} positive_player_team_rows={positive}")
    print(f"sample_person_team_ids={sample}")


def main() -> int:
    computed = current_season()
    print(f"current_season() -> {computed!r}")
    _describe("hardcoded-default", "2024-25")
    _describe("dynamic-current", computed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
