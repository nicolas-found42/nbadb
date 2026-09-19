from __future__ import annotations

from typing import ClassVar

from nbadb.transform.base import SqlTransformer

# Every stat category AllTimeLeadersGrids returns, in the order the star schema
# exposes them: the three originally-modeled career totals, then the remaining
# sixteen box-score categories in traditional box-score column order.
_CATEGORIES: tuple[str, ...] = (
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

_CATEGORY_LABELS: dict[str, str] = {
    "pts": "points",
    "ast": "assists",
    "reb": "rebounds",
    "fgm": "field goals made",
    "fga": "field goals attempted",
    "fg_pct": "field goal percentage",
    "fg3m": "three-pointers made",
    "fg3a": "three-pointers attempted",
    "fg3_pct": "three-point percentage",
    "ftm": "free throws made",
    "fta": "free throws attempted",
    "ft_pct": "free throw percentage",
    "oreb": "offensive rebounds",
    "dreb": "defensive rebounds",
    "blk": "blocks",
    "stl": "steals",
    "tov": "turnovers",
    "pf": "personal fouls",
    "gp": "games played",
}


def _rows_cte(category: str) -> str:
    return f"""{category}_rows AS (
            SELECT DISTINCT
                player_id,
                player_name,
                {category},
                {category}_rank
            FROM stg_all_time_{category}
        )"""


def _source_cte(category: str) -> str:
    label = _CATEGORY_LABELS[category]
    return f"""{category}_source AS (
            SELECT
                CASE WHEN player_id IS NULL
                    THEN error('all-time {label} source has null player_id')
                    ELSE player_id END AS player_id,
                CASE WHEN COUNT(DISTINCT {category}) > 1
                    THEN error('conflicting all-time {label} values')
                    ELSE MIN({category}) END AS {category},
                CASE WHEN COUNT(DISTINCT {category}_rank) > 1
                    THEN error('conflicting all-time {label} ranks')
                    ELSE MIN({category}_rank) END AS {category}_rank
            FROM {category}_rows
            GROUP BY player_id
        )"""


def _name_authority_cte() -> str:
    name_rows = "\n            UNION ALL\n            ".join(
        f"SELECT player_id, player_name FROM {category}_rows" for category in _CATEGORIES
    )
    return f"""name_rows AS (
            {name_rows}
        ), name_authority AS (
            SELECT
                player_id,
                CASE WHEN COUNT(DISTINCT player_name) > 1
                    THEN error('conflicting all-time player names')
                    ELSE MIN(player_name) END AS player_name
            FROM name_rows
            GROUP BY player_id
        )"""


def _metric_authority_cte() -> str:
    join_lines = [f"FROM {_CATEGORIES[0]}_source"]
    prior: list[str] = [_CATEGORIES[0]]
    for category in _CATEGORIES[1:]:
        id_expr = (
            f"{prior[0]}_source.player_id"
            if len(prior) == 1
            else f"COALESCE({', '.join(f'{p}_source.player_id' for p in prior)})"
        )
        join_lines.append(
            f"FULL OUTER JOIN {category}_source\n"
            f"                ON {id_expr} = {category}_source.player_id"
        )
        prior.append(category)
    join_sql = "\n            ".join(join_lines)

    id_coalesce = ", ".join(f"{category}_source.player_id" for category in _CATEGORIES)
    value_cols = ",\n                ".join(
        f"{category}_source.{category}" for category in _CATEGORIES
    )
    rank_cols = ",\n                ".join(
        f"{category}_source.{category}_rank" for category in _CATEGORIES
    )
    return f"""metric_authority AS (
            SELECT
                COALESCE({id_coalesce}) AS player_id,
                {value_cols},
                {rank_cols}
            {join_sql}
        )"""


def _final_select() -> str:
    value_cols = ",\n            ".join(f"metric_authority.{category}" for category in _CATEGORIES)
    rank_cols = ",\n            ".join(
        f"metric_authority.{category}_rank" for category in _CATEGORIES
    )
    return f"""SELECT
            metric_authority.player_id,
            name_authority.player_name,
            {value_cols},
            {rank_cols}
        FROM metric_authority
        LEFT JOIN name_authority
            ON metric_authority.player_id = name_authority.player_id
        ORDER BY metric_authority.player_id"""


def _build_sql() -> str:
    ctes = [_rows_cte(category) for category in _CATEGORIES]
    ctes.extend(_source_cte(category) for category in _CATEGORIES)
    ctes.append(_name_authority_cte())
    ctes.append(_metric_authority_cte())
    body = ", ".join(ctes)
    return f"""
        WITH {body}
        {_final_select()}
    """


class AggAllTimeLeadersTransformer(SqlTransformer):
    output_table: ClassVar[str] = "agg_all_time_leaders"
    depends_on: ClassVar[list[str]] = [
        "stg_all_time_pts",
        "stg_all_time_ast",
        "stg_all_time_reb",
        "stg_all_time_fgm",
        "stg_all_time_fga",
        "stg_all_time_fg_pct",
        "stg_all_time_fg3m",
        "stg_all_time_fg3a",
        "stg_all_time_fg3_pct",
        "stg_all_time_ftm",
        "stg_all_time_fta",
        "stg_all_time_ft_pct",
        "stg_all_time_oreb",
        "stg_all_time_dreb",
        "stg_all_time_blk",
        "stg_all_time_stl",
        "stg_all_time_tov",
        "stg_all_time_pf",
        "stg_all_time_gp",
    ]

    _SQL: ClassVar[str] = _build_sql()
