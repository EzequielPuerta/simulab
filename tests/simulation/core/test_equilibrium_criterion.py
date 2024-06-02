import pytest

from src.simulation.core.equilibrium_criterion import EquilibriumCriterion, WithoutCriterion

series = lambda values: {"test_series": values}


def test_without_criterion() -> None:
    criterion = WithoutCriterion()
    assert not criterion.in_equilibrium(series([]))
    assert not criterion.in_equilibrium(series([1]))
    assert not criterion.in_equilibrium(series([1, 2]))
    assert not criterion.in_equilibrium(series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
    assert not criterion.in_equilibrium(series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]))
    balanced = criterion.in_equilibrium(
        series([1, 2.99, 3.00, 3.01, 3.00, 3.01, 3.01, 3.02, 3.03, 3.02, 3.01, 3.02])
    )
    assert not balanced


def test_equilibrium_criterion_without_series_name_raises_exception() -> None:
    with pytest.raises(TypeError) as error_msg:
        EquilibriumCriterion()  # type: ignore[call-arg]
    assert (
        error_msg.value.args[0]
        == "EquilibriumCriterion.__init__() missing 1 required positional argument: 'series_name'"
    )


def test_equilibrium_criterion_with_default_values() -> None:
    criterion = EquilibriumCriterion(series_name="test_series")
    assert criterion.series_name == "test_series"
    assert criterion.window_size == 20
    assert criterion.tolerance == 0.001


def test_equilibrium_criterion_with_custom_values() -> None:
    criterion = EquilibriumCriterion("test_series", 10, 0.01)
    assert criterion.series_name == "test_series"
    assert criterion.window_size == 10
    assert criterion.tolerance == 0.01


def test_equilibrium_criterion_with_wrong_series_name() -> None:
    available_series = {"mock_series": [1, 2, 3, 4, 5]}
    criterion = EquilibriumCriterion(series_name="test_series")
    with pytest.raises(AssertionError):
        criterion.in_equilibrium(available_series)


def test_equilibrium_criterion_not_in_equilibrium() -> None:
    criterion = EquilibriumCriterion("test_series", 10, 0.01)
    assert not criterion.in_equilibrium(series([]))
    assert not criterion.in_equilibrium(series([1]))
    assert not criterion.in_equilibrium(series([1, 2]))
    assert not criterion.in_equilibrium(series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]))
    assert not criterion.in_equilibrium(series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]))


def test_equilibrium_criterion_in_equilibrium() -> None:
    criterion = EquilibriumCriterion("test_series", 10, 0.01)
    balanced = criterion.in_equilibrium(
        series([1, 2.99, 3.00, 3.01, 3.00, 3.01, 3.01, 3.02, 3.03, 3.02, 3.01, 3.02])
    )
    assert balanced
