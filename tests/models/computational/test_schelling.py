import pytest

from src.models.computational.schelling.model import Schelling
from src.simulation.core.equilibrium_criterion import WithoutCriterion
from src.simulation.core.experiment import ExperimentParametersSet
from src.simulation.core.neighborhood import Moore
from src.simulation.core.runner import Runner

experiment_parameters_set = ExperimentParametersSet(
    length=[10],
    tolerance=[3, 4, 5],
    neighborhood=[Moore],
)
runner = Runner(
    Schelling,
    experiment_parameters_set,
    WithoutCriterion(),
    max_steps=5,
)


def test_schelling() -> None:
    assert len(runner.experiments) == 3
    with pytest.raises(AttributeError):
        runner.experiments[0].series

    runner.start()
    for series in runner.experiments[0].series.values():
        assert len(series) == 5 + 1
