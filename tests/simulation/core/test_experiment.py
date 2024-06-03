import pytest

from simulab.simulation.core.experiment import ExperimentParameters, ExperimentParametersSet


def test_experiment_parameters_creation() -> None:
    length = 30
    tolerance = 5
    data = {"length": length, "tolerance": tolerance}
    parameters = ExperimentParameters(**data)

    assert parameters.length == length
    assert parameters.length == parameters["length"]
    assert parameters.tolerance == tolerance
    assert parameters.tolerance == parameters["tolerance"]


def test_experiment_parameters_equality() -> None:
    data1 = {"length": 30, "tolerance": 5}
    data2 = {"length": 30, "tolerance": 6}
    assert ExperimentParameters(**data1) == ExperimentParameters(**data1)
    assert ExperimentParameters(**data1) != ExperimentParameters(**data2)


def test_experiment_parameters_set_wrong_creation() -> None:
    with pytest.raises(TypeError) as error_msg:
        ExperimentParametersSet(**{1: [1]})  # type: ignore[misc]
    assert error_msg.value.args[0] == "keywords must be strings"

    with pytest.raises(AssertionError) as error_msg:
        ExperimentParametersSet(**{"mock_parameter": 1})
    assert error_msg.value.args[0] == "Experiment parameters should be passed using lists."


def test_experiment_parameters_set_creation() -> None:
    lengths = [20, 30]
    tolerances = [4, 5, 6]
    data = {"length": lengths, "tolerance": tolerances}
    parameters_set = ExperimentParametersSet(**data)

    _expected_parameters = [
        (20, 4),
        (20, 5),
        (20, 6),
        (30, 4),
        (30, 5),
        (30, 6),
    ]
    expected_parameters = [
        ExperimentParameters(length=each[0], tolerance=each[1]) for each in _expected_parameters
    ]

    assert len(parameters_set) == len(lengths) * len(tolerances)
    assert len(parameters_set) == len(expected_parameters)
    assert all((parameters in expected_parameters for parameters in parameters_set))


def test_experiment_parameters_set_get_item() -> None:
    lengths = [20, 30]
    tolerances = [4, 5, 6]
    data = {"length": lengths, "tolerance": tolerances}
    parameters_set = ExperimentParametersSet(**data)
    assert parameters_set["length"] == lengths
    assert parameters_set["tolerance"] == tolerances


def test_experiment_parameters_set_parameters_to_vary() -> None:
    lengths = [20]
    tolerances = [4, 5, 6]
    data = {"length": lengths, "tolerance": tolerances}
    parameters_set = ExperimentParametersSet(**data)
    assert parameters_set.parameters_to_vary == ["tolerance"]

    lengths = [20, 30]
    tolerances = [4, 5, 6]
    data = {"length": lengths, "tolerance": tolerances}
    parameters_set = ExperimentParametersSet(**data)
    assert parameters_set.parameters_to_vary == ["length", "tolerance"]
