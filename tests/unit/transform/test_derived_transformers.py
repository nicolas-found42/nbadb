"""Tests for derived transformers: agg_player_season, agg_team_season, agg_player_rolling.

Verify column fixes (team_id inclusion) and dependency declarations.
"""

from __future__ import annotations

import duckdb
import polars as pl
import pytest

# ---------------------------------------------------------------------------
# Dependency declaration tests
# ---------------------------------------------------------------------------


def test_agg_player_season_has_dim_game_dependency():
    from nbadb.transform.derived.agg_player_season import AggPlayerSeasonTransformer

    assert "dim_game" in AggPlayerSeasonTransformer.depends_on


def test_agg_player_season_has_dim_team_dependency():
    from nbadb.transform.derived.agg_player_season import AggPlayerSeasonTransformer

    assert "dim_team" in AggPlayerSeasonTransformer.depends_on


def test_agg_player_rolling_has_dim_game_dependency():
    from nbadb.transform.derived.agg_player_rolling import AggPlayerRollingTransformer

    assert AggPlayerRollingTransformer.depends_on == [
        "fact_player_game_traditional",
        "dim_game",
    ]


def test_agg_team_season_has_dim_game_dependency():
    from nbadb.transform.derived.agg_team_season import AggTeamSeasonTransformer

    assert "dim_game" in AggTeamSeasonTransformer.depends_on


def test_dim_player_no_phantom_dependency():
    from nbadb.transform.dimensions.dim_player import DimPlayerTransformer

    assert "stg_player_career" not in DimPlayerTransformer.depends_on


# ---------------------------------------------------------------------------
# Functional test: agg_player_season includes team_id
# ---------------------------------------------------------------------------


def test_agg_player_season_no_unused_misc_dependency():
    """fact_player_game_misc should not be in depends_on (unused in SQL)."""
    from nbadb.transform.derived.agg_player_season import AggPlayerSeasonTransformer

    assert "fact_player_game_misc" not in AggPlayerSeasonTransformer.depends_on


def test_agg_team_pace_has_dim_game_dependency():
    from nbadb.transform.derived.agg_team_pace_and_efficiency import (
        AggTeamPaceAndEfficiencyTransformer,
    )

    assert "dim_game" in AggTeamPaceAndEfficiencyTransformer.depends_on


def test_agg_shot_zones_has_dim_game_dependency():
    from nbadb.transform.derived.agg_shot_zones import AggShotZonesTransformer

    assert "dim_game" in AggShotZonesTransformer.depends_on


def test_agg_player_season_per48_output_table():
    from nbadb.transform.derived.agg_player_season_per48 import (
        AggPlayerSeasonPer48Transformer,
    )

    assert AggPlayerSeasonPer48Transformer.output_table == "agg_player_season_per48"


def test_agg_player_season_includes_team_id():
    """After fix, agg_player_season should include team_id in output."""
    from nbadb.transform.derived.agg_player_season import AggPlayerSeasonTransformer

    transformer = AggPlayerSeasonTransformer()

    fact_trad = pl.DataFrame(
        {
            "player_id": [101, 101],
            "game_id": [1001, 1002],
            "team_id": [1, 1],
            "min": [30.0, 28.0],
            "pts": [25, 20],
            "reb": [5, 6],
            "ast": [7, 5],
            "stl": [2, 1],
            "blk": [1, 0],
            "tov": [3, 2],
            "fgm": [9, 8],
            "fga": [18, 17],
            "fg_pct": [0.5, 0.47],
            "fg3m": [3, 2],
            "fg3a": [7, 6],
            "fg3_pct": [0.43, 0.33],
            "ftm": [4, 2],
            "fta": [5, 3],
            "ft_pct": [0.8, 0.67],
            "oreb": [1, 2],
            "dreb": [4, 4],
            "pf": [2, 3],
            "plus_minus": [10, -2],
        }
    )
    fact_adv = pl.DataFrame(
        {
            "player_id": [101, 101],
            "game_id": [1001, 1002],
            "team_id": [1, 1],
            "poss": [45.0, 42.0],
            "off_rating": [115.0, 108.0],
            "def_rating": [105.0, 110.0],
            "net_rating": [10.0, -2.0],
            "ast_pct": [0.3, 0.25],
            "ast_ratio": [0.25, 0.2],
            "reb_pct": [0.1, 0.12],
            "oreb_pct": [0.05, 0.07],
            "dreb_pct": [0.15, 0.14],
            "efg_pct": [0.55, 0.5],
            "ts_pct": [0.6, 0.55],
            "pace": [100.0, 98.0],
            "pie": [0.15, 0.1],
            "usg_pct": [0.28, 0.25],
        }
    )
    dim_game = pl.DataFrame(
        {
            "game_id": [1001, 1002],
            "game_date": ["2024-01-15", "2024-01-17"],
            "season_year": [2024, 2024],
            "season_type": ["Regular Season", "Regular Season"],
            "home_team_id": [1, 2],
            "visitor_team_id": [2, 1],
            "matchup": ["TST vs OPP", "OPP vs TST"],
            "arena_name": ["Arena A", "Arena B"],
            "arena_city": ["City A", "City B"],
        }
    )

    dim_team = pl.DataFrame(
        {
            "team_id": [1, 2],
            "abbreviation": ["TST", "OPP"],
            "full_name": ["Test Team", "Opponent Team"],
            "city": ["Test City", "Opp City"],
            "state": ["TS", "OP"],
            "arena": ["Test Arena", "Opp Arena"],
            "year_founded": [2000, 2000],
            "conference": ["East", "West"],
            "division": ["Atlantic", "Pacific"],
        }
    )

    staging = {
        "fact_player_game_traditional": fact_trad.lazy(),
        "fact_player_game_advanced": fact_adv.lazy(),
        "dim_game": dim_game.lazy(),
        "dim_team": dim_team.lazy(),
    }

    conn = duckdb.connect()
    for key, val in staging.items():
        conn.register(key, val.collect())
    transformer._conn = conn

    result = transformer.transform(staging)

    assert "team_id" in result.columns, f"team_id missing from output: {result.columns}"
    assert "team_abbreviation" in result.columns, (
        f"team_abbreviation missing from output: {result.columns}"
    )
    assert result.shape[0] == 1  # grouped by player, team, season, type
    assert result["team_id"][0] == 1
    assert result["team_abbreviation"][0] == "TST"
    conn.close()


_ALL_TIME_CATEGORIES = (
    "pts",
    "ast",
    "reb",
    "fgm",
    "fga",
    "fg_pct",
    "fg3m",
    "fg3a",
    "fg3_pct",
    "ftm",
    "fta",
    "ft_pct",
    "oreb",
    "dreb",
    "blk",
    "stl",
    "tov",
    "pf",
    "gp",
)

_ALL_TIME_PCT_CATEGORIES = frozenset({"fg_pct", "fg3_pct", "ft_pct"})

_ALL_TIME_ROW = tuple[int | None, str | None, float | None, int | None]


def _all_time_frame(
    stat: str,
    rows: list[_ALL_TIME_ROW],
) -> pl.DataFrame:
    value_dtype = pl.Float64 if stat in _ALL_TIME_PCT_CATEGORIES else pl.Int64
    return pl.DataFrame(
        rows,
        schema={
            "player_id": pl.Int64,
            "player_name": pl.String,
            stat: value_dtype,
            f"{stat}_rank": pl.Int64,
        },
        orient="row",
    )


def _all_time_value(category: str, index: int) -> int | float:
    if category in _ALL_TIME_PCT_CATEGORIES:
        return round(0.3 + index * 0.01, 3)
    return 1000 + index


def _run_all_time_leaders(
    rows_by_source: dict[str, list[_ALL_TIME_ROW]],
) -> pl.DataFrame:
    from nbadb.transform.derived.agg_all_time_leaders import (
        AggAllTimeLeadersTransformer,
    )

    conn = duckdb.connect()
    try:
        staging: dict[str, pl.LazyFrame] = {}
        for stat in _ALL_TIME_CATEGORIES:
            frame = _all_time_frame(stat, rows_by_source.get(stat, []))
            table_name = f"stg_all_time_{stat}"
            conn.register(table_name, frame)
            staging[table_name] = frame.lazy()
        transformer = AggAllTimeLeadersTransformer()
        transformer._conn = conn
        return transformer.transform(staging)
    finally:
        conn.close()


def _all_time_row(player_id: int | None, player_name: str | None, **overrides: int | float) -> dict:
    """Build a full 40-column expected row with unset stat/rank fields as None."""
    row: dict = {"player_id": player_id, "player_name": player_name}
    for category in _ALL_TIME_CATEGORIES:
        row[category] = overrides.get(category)
    for category in _ALL_TIME_CATEGORIES:
        row[f"{category}_rank"] = overrides.get(f"{category}_rank")
    return row


def test_agg_all_time_leaders_uses_only_representable_sources_and_projection() -> None:
    from nbadb.transform.derived.agg_all_time_leaders import (
        AggAllTimeLeadersTransformer,
    )

    assert AggAllTimeLeadersTransformer.depends_on == [
        f"stg_all_time_{category}" for category in _ALL_TIME_CATEGORIES
    ]
    normalized_sql = " ".join(AggAllTimeLeadersTransformer._SQL.lower().split())
    assert "select *" not in normalized_sql
    assert "stat_category" not in normalized_sql
    assert "from stg_all_time " not in normalized_sql
    referenced_all_time_sources = {
        token.strip(",()") for token in normalized_sql.split() if token.startswith("stg_all_time")
    }
    assert referenced_all_time_sources == set(AggAllTimeLeadersTransformer.depends_on)


def test_agg_all_time_leaders_consolidates_nineteen_categories_at_player_grain() -> None:
    from nbadb.schemas.star.agg_schemas import AggAllTimeLeadersSchema

    rows_by_source = {
        category: [(2544, "LeBron James", _all_time_value(category, index), index + 1)]
        for index, category in enumerate(_ALL_TIME_CATEGORIES)
    }
    result = _run_all_time_leaders(rows_by_source)

    expected_columns = (
        ["player_id", "player_name"]
        + list(_ALL_TIME_CATEGORIES)
        + [f"{category}_rank" for category in _ALL_TIME_CATEGORIES]
    )
    assert result.columns == expected_columns

    overrides = {
        category: _all_time_value(category, index)
        for index, category in enumerate(_ALL_TIME_CATEGORIES)
    }
    overrides.update(
        {f"{category}_rank": index + 1 for index, category in enumerate(_ALL_TIME_CATEGORIES)}
    )
    assert result.to_dicts() == [_all_time_row(2544, "LeBron James", **overrides)]
    assert result.unique(subset=["player_id"]).height == result.height
    assert AggAllTimeLeadersSchema.validate(result).to_dicts() == result.to_dicts()
    assert list(AggAllTimeLeadersSchema.to_schema().columns) == result.columns


def test_agg_all_time_leaders_full_outer_join_preserves_disjoint_membership() -> None:
    result = _run_all_time_leaders(
        {
            "pts": [(1, "Points", 100, 1)],
            "ast": [(2, "Assists", 80, 2)],
            "reb": [(3, "Rebounds", 70, 3)],
        }
    )

    assert result.to_dicts() == [
        _all_time_row(1, "Points", pts=100, pts_rank=1),
        _all_time_row(2, "Assists", ast=80, ast_rank=2),
        _all_time_row(3, "Rebounds", reb=70, reb_rank=3),
    ]


def test_agg_all_time_leaders_exact_duplicates_and_null_plus_known_are_idempotent() -> None:
    result = _run_all_time_leaders(
        {
            "pts": [
                (1, None, None, None),
                (1, "Known", 100, 1),
                (1, "Known", 100, 1),
            ],
            "ast": [(1, None, None, None)],
        }
    )

    assert result.to_dicts() == [_all_time_row(1, "Known", pts=100, pts_rank=1)]


def test_agg_all_time_leaders_all_null_name_is_preserved_as_null() -> None:
    result = _run_all_time_leaders(
        {
            "pts": [(1, None, 100, 1)],
            "ast": [(1, None, 80, 2)],
            "reb": [(1, None, 70, 3)],
        }
    )

    assert result["player_name"].to_list() == [None]


@pytest.mark.parametrize(
    ("source", "rows", "message"),
    [
        ("pts", [(1, "Known", 100, 1), (1, "Known", 101, 1)], "points values"),
        ("pts", [(1, "Known", 100, 1), (1, "Known", 100, 2)], "points ranks"),
        ("ast", [(1, "Known", 80, 1), (1, "Known", 81, 1)], "assists values"),
        ("ast", [(1, "Known", 80, 1), (1, "Known", 80, 2)], "assists ranks"),
        ("reb", [(1, "Known", 70, 1), (1, "Known", 71, 1)], "rebounds values"),
        ("reb", [(1, "Known", 70, 1), (1, "Known", 70, 2)], "rebounds ranks"),
        ("gp", [(1, "Known", 70, 1), (1, "Known", 71, 1)], "games played values"),
        ("fg_pct", [(1, "Known", 70, 1), (1, "Known", 71, 1)], "field goal percentage values"),
    ],
)
def test_agg_all_time_leaders_conflicting_metric_or_rank_fails_closed(
    source: str,
    rows: list[_ALL_TIME_ROW],
    message: str,
) -> None:
    with pytest.raises(duckdb.Error, match=message):
        _run_all_time_leaders({source: rows})


def test_agg_all_time_leaders_conflicting_name_across_sources_fails_closed() -> None:
    with pytest.raises(duckdb.Error, match="conflicting all-time player names"):
        _run_all_time_leaders(
            {
                "pts": [(1, "First Name", 100, 1)],
                "ast": [(1, "Second Name", 80, 1)],
            }
        )


@pytest.mark.parametrize("source", ["pts", "ast", "reb", "gp"])
def test_agg_all_time_leaders_null_player_id_fails_closed(source: str) -> None:
    with pytest.raises(duckdb.Error, match="null player_id"):
        _run_all_time_leaders({source: [(None, "Unknown", 1, 1)]})
