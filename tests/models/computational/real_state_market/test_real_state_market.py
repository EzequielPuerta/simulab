import pytest

from src.models.computational.real_state_market.model import RealStateMarket
from src.simulation.core.equilibrium_criterion import WithoutCriterion
from src.simulation.core.experiment import ExperimentParametersSet
from src.simulation.core.neighborhood import Moore
from src.simulation.core.runner import Runner

experiment_parameters_set = ExperimentParametersSet(
    length=[10],
    alpha=[0.1, 0.3, 0.7, 0.9],
    neighborhood=[Moore],
    agent_types=[2],
)
runner = Runner(
    RealStateMarket,
    experiment_parameters_set,
    WithoutCriterion(),
    max_steps=5,
)


def test_real_state_market() -> None:
    assert len(runner.experiments) == 4
    with pytest.raises(AttributeError):
        runner.experiments[0].series

    runner.start()
    for series in runner.experiments[0].series.values():
        assert len(series) == 5 + 1
