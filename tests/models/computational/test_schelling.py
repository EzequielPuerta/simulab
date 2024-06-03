import pytest

from simulab.models.computational.schelling.model import Schelling
from simulab.simulation.core.equilibrium_criterion import WithoutCriterion
from simulab.simulation.core.experiment import ExperimentParametersSet
from simulab.simulation.core.neighborhood import ExpandedMoore
from simulab.simulation.core.runner import Runner

experiment_parameters_set = ExperimentParametersSet(
    length=[10],
    tolerance=[3, 4, 5],
    neighborhood=[ExpandedMoore(vision_range=1)],
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
