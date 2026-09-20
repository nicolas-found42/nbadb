from __future__ import annotations

import pytest

from nbadb.core.nba_api_observed_columns import (
    ADMITTED_COLUMNS,
    UPSTREAM_COMMIT,
    UPSTREAM_VERSION,
    admitted_result_set_columns,
)
from nbadb.core.nba_api_provenance import NBA_API_UPSTREAM_COMMIT
from nbadb.core.nba_api_runtime_contract import pinned_runtime_contracts


def test_absent_entry_returns_the_generated_columns_unchanged() -> None:
    generated = ("ID", "VALUE")

    assert admitted_result_set_columns("NoSuchEndpoint", "NoSuchSet", generated, frozenset()) == (
        generated
    )


def test_only_admitted_columns_the_response_carries_are_added() -> None:
    """Admitted columns are optional, not a fixed superset.

    NBA serves PlayerGameLogs' FP_HIGH_SCORE columns for the current season but
    not for historical ones. Pinning them as always-required turns an ordinary
    historical response into removed_header, which is how this first showed up.
    """
    generated = ("PLAYER_ID",)

    both = admitted_result_set_columns(
        "PlayerGameLogs",
        "PlayerGameLogs",
        generated,
        frozenset({"NICKNAME", "FP_HIGH_SCORE", "MIN_SEC"}),
    )
    assert set(both) == {"PLAYER_ID", "NICKNAME", "FP_HIGH_SCORE", "MIN_SEC"}
    assert both[0] == "PLAYER_ID"

    historical = admitted_result_set_columns(
        "PlayerGameLogs",
        "PlayerGameLogs",
        generated,
        frozenset({"NICKNAME", "MIN_SEC"}),
    )
    assert set(historical) == {"PLAYER_ID", "NICKNAME", "MIN_SEC"}
    assert "FP_HIGH_SCORE" not in historical


def test_none_present_returns_the_generated_columns_unchanged() -> None:
    generated = ("PLAYER_ID",)

    assert (
        admitted_result_set_columns("PlayerGameLogs", "PlayerGameLogs", generated, frozenset())
        == generated
    )


def test_entry_already_carried_by_the_generated_contract_is_rejected() -> None:
    """A redundant entry means upstream caught up and the pin must be deleted."""
    with pytest.raises(ValueError, match="must be removed"):
        admitted_result_set_columns(
            "PlayerIndex",
            "PlayerIndex",
            ("PERSON_ID", "SUPPLEMENTAL_STATUS"),
            frozenset({"SUPPLEMENTAL_STATUS"}),
        )


def test_every_admitted_entry_is_still_absent_from_the_generated_contract() -> None:
    """Freshness guard: an entry upstream now documents would mask a real removal."""
    contracts = pinned_runtime_contracts()

    for runtime_class_name, result_sets in ADMITTED_COLUMNS.items():
        contract = contracts.get(runtime_class_name)
        assert contract is not None, f"{runtime_class_name} is not a pinned runtime endpoint"
        generated_by_name = {
            rs.result_set_name: set(rs.expected_columns) for rs in contract.result_sets
        }
        for result_set_name, admitted in result_sets.items():
            generated = generated_by_name.get(result_set_name)
            assert generated is not None, (
                f"{runtime_class_name}.{result_set_name} is not a pinned result set"
            )
            assert admitted, f"{runtime_class_name}.{result_set_name} admits nothing"
            redundant = sorted(set(admitted) & generated)
            assert not redundant, (
                f"{runtime_class_name}.{result_set_name} admits columns the generated "
                f"contract already carries; delete them: {redundant}"
            )


def test_provenance_matches_the_pinned_upstream_release() -> None:
    """The table is only meaningful against the upstream it was diffed from."""
    assert UPSTREAM_COMMIT == NBA_API_UPSTREAM_COMMIT
    assert UPSTREAM_VERSION == "1.11.4"
