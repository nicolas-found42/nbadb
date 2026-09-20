"""Dated local pins for provider columns `nba_api` does not yet document.

The pinned runtime contract is generated from `nba_api`'s own endpoint docs at
the tag of the installed release. NBA sometimes serves columns that those docs
have not caught up with, and when that happens the generated contract cannot
express the real response: the adapter classifies it as `additive_header`,
demotes a complete response to a lossless fallback, and every caller sees a
zero-width frame. As of `nba-api 1.11.4` -- the latest release, upstream commit
`e0295f8333c3496b5754dbffbdf4c1c1dee3c2f4` -- four endpoints are in that state, two of which
(`PlayerGameLogs`, `PlayerIndex`) are the primary and fallback sources for
player/team discovery, so the extraction chain cannot run without them.

This table admits those columns, and only those columns, by name.

Contract:

* **Additive only.** An entry may only add columns to the generated pin. It can
  never remove, rename or reorder one, and `admitted_result_set_columns` raises
  if a generated column is missing from the result.
* **Closed.** Anything the provider sends beyond the generated pin plus the
  columns enumerated here is still `additive_header`, still fatal. This widens
  the contract by an enumerated delta, it does not disable the check.
* **Order-free.** Only names are pinned. The adapter already admits a pure
  permutation of a known column set, so a provider reordering does not
  invalidate these entries.
* **Freshness trigger.** Re-derive this table whenever `nba-api` is upgraded: a
  release that documents one of these columns makes its entry redundant, and a
  stale entry would mask a genuine removal upstream. Delete entries that the
  generated contract has caught up with.

Observed 2026-09-19 against live `stats.nba.com`, by diffing each endpoint's
live headers against `pinned_endpoint_contract(...).result_sets`.
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping

__all__ = [
    "ADMITTED_COLUMNS",
    "OBSERVED_AT",
    "UPSTREAM_COMMIT",
    "UPSTREAM_VERSION",
    "admitted_result_set_columns",
]

OBSERVED_AT: Final[str] = "2026-09-19"
UPSTREAM_VERSION: Final[str] = "1.11.4"
UPSTREAM_COMMIT: Final[str] = "e0295f8333c3496b5754dbffbdf4c1c1dee3c2f4"

_ADMITTED: Final[dict[str, dict[str, tuple[str, ...]]]] = {
    "AllTimeLeadersGrids": {
        "ASTLeaders": ("IS_ACTIVE_FLAG",),
        "BLKLeaders": ("IS_ACTIVE_FLAG",),
        "DREBLeaders": ("IS_ACTIVE_FLAG",),
        "FG3ALeaders": ("IS_ACTIVE_FLAG",),
        "FG3MLeaders": ("IS_ACTIVE_FLAG",),
        "FG3_PCTLeaders": ("IS_ACTIVE_FLAG",),
        "FGALeaders": ("IS_ACTIVE_FLAG",),
        "FGMLeaders": ("IS_ACTIVE_FLAG",),
        "FG_PCTLeaders": ("IS_ACTIVE_FLAG",),
        "FTALeaders": ("IS_ACTIVE_FLAG",),
        "FTMLeaders": ("IS_ACTIVE_FLAG",),
        "FT_PCTLeaders": ("IS_ACTIVE_FLAG",),
        "GPLeaders": ("IS_ACTIVE_FLAG",),
        "OREBLeaders": ("IS_ACTIVE_FLAG",),
        "PFLeaders": ("IS_ACTIVE_FLAG",),
        "PTSLeaders": ("IS_ACTIVE_FLAG",),
        "REBLeaders": ("IS_ACTIVE_FLAG",),
        "STLLeaders": ("IS_ACTIVE_FLAG",),
        "TOVLeaders": ("IS_ACTIVE_FLAG",),
    },
    "BoxScoreTraditionalV2": {
        "PlayerStats": ("NICKNAME",),
    },
    "DraftHistory": {
        "DraftHistory": ("PLAYER_PROFILE_FLAG",),
    },
    "LeagueDashLineups": {
        "Lineups": ("SUM_TIME_PLAYED",),
    },
    "LeagueLeaders": {
        "LeagueLeaders": ("TEAM_ID",),
    },
    "LeagueLineupViz": {
        "LeagueLineupViz": ("SUM_TM_MIN",),
    },
    "PlayerGameLogs": {
        "PlayerGameLogs": (
            "NICKNAME",
            "WNBA_FANTASY_PTS",
            "FP_HIGH_SCORE",
            "WNBA_FANTASY_PTS_RANK",
            "FP_HIGH_SCORE_RANK",
            "AVAILABLE_FLAG",
            "MIN_SEC",
            "TEAM_COUNT",
        ),
    },
    "PlayerIndex": {
        "PlayerIndex": ("SUPPLEMENTAL_STATUS",),
    },
    "TeamDashLineups": {
        "Lineups": ("SUM_TIME_PLAYED",),
    },
    "TeamGameLogs": {
        "TeamGameLogs": ("AVAILABLE_FLAG",),
    },
    "TeamPlayerDashboard": {
        "PlayersSeasonTotals": (
            "NICKNAME",
            "WNBA_FANTASY_PTS",
            "FP_HIGH_SCORE",
            "WNBA_FANTASY_PTS_RANK",
            "FP_HIGH_SCORE_RANK",
            "TEAM_COUNT",
        ),
    },
}

ADMITTED_COLUMNS: Final[Mapping[str, Mapping[str, tuple[str, ...]]]] = MappingProxyType(
    {name: MappingProxyType(dict(sets)) for name, sets in _ADMITTED.items()}
)


def admitted_result_set_columns(
    runtime_class_name: str,
    result_set_name: str,
    generated: tuple[str, ...],
    observed: frozenset[str],
) -> tuple[str, ...]:
    """Return `generated` widened by the admitted columns this response carries.

    Admitted columns are *optional*: NBA serves some of them only for certain
    requests -- `PlayerGameLogs` returns `FP_HIGH_SCORE` and `FP_HIGH_SCORE_RANK`
    for the current season but not for historical ones -- so pinning them as
    always-required would turn an ordinary historical response into
    `removed_header`. Only the admitted columns actually present in `observed`
    are added, which keeps the widening exact for each response while leaving
    every generated column required.

    Returns `generated` unchanged when nothing is admitted or present. Raises
    `ValueError` when an entry has gone stale -- the generated contract already
    carries the column, so upstream caught up and the entry must be deleted.
    """

    admitted = ADMITTED_COLUMNS.get(runtime_class_name, {}).get(result_set_name)
    if not admitted:
        return generated
    overlap = [column for column in admitted if column in generated]
    if overlap:
        raise ValueError(
            f"admitted columns for {runtime_class_name}.{result_set_name} are already in "
            f"the generated contract and must be removed: {sorted(overlap)}"
        )
    if len(set(admitted)) != len(admitted):
        raise ValueError(
            f"admitted columns for {runtime_class_name}.{result_set_name} contain duplicates"
        )
    present = tuple(column for column in admitted if column in observed)
    return (*generated, *present) if present else generated
