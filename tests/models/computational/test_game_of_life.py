import pytest

from simulab.models.computational.game_of_life.model import GameOfLife
from simulab.models.computational.game_of_life.seeds import Blinker
from simulab.simulation.core.equilibrium_criterion import WithoutCriterion
from simulab.simulation.core.experiment import ExperimentParametersSet
from simulab.simulation.core.neighborhood import Moore
from simulab.simulation.core.runner import Runner

experiment_parameters_set = ExperimentParametersSet(
    length=[30, 40],
    neighborhood=[Moore],
    seeds=[[Blinker(25, 25)]],
)
runner = Runner(
    GameOfLife,
    experiment_parameters_set,
    WithoutCriterion(),
    max_steps=5,
)


def test_real_state_market() -> None:
    assert len(runner.experiments) == 2
    with pytest.raises(AttributeError):
        runner.experiments[0].series

    runner.start()
    for series in runner.experiments[0].series.values():
        assert len(series) == 5 + 1
