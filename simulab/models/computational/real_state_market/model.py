from typing import List, Tuple
from typing import cast as typing_cast

from simulab.models.abstract.agent import Agent
from simulab.models.abstract.model import AbstractLatticeModel, as_series, as_series_with
from simulab.models.computational.real_state_market.agent import RealStateAgent
from simulab.models.computational.real_state_market.formulas import PriceFormula, UtilityFormula
from simulab.simulation.core.lattice import Lattice


class RealStateMarket(AbstractLatticeModel):
    def __init__(  # type: ignore[no-untyped-def]
        self,
        alpha: float = 0.5,
        A: float = 1 / 16,
        B: float = 0.5,
        utility_tolerance: float = 0.85,
        *args,
        **kwargs,
    ):
        super(RealStateMarket, self).__init__(*args, **kwargs)
        self.alpha = alpha
        self.A = A
        self.B = B
        self.utility_tolerance = utility_tolerance
        self.__utility_formula = UtilityFormula(self.alpha)
        self.__price_formula = PriceFormula(self.A, self.B, self.neighborhood.size())

    def _create_agent(self, basic_agent: Agent, i: int, j: int) -> RealStateAgent:
        similar_amount = self.similar_neighbors_amount(i, j, count_myself=True)
        initial_capital = 1.0
        property_price = self.property_price(similar_amount)
        return RealStateAgent(
            agent_type=basic_agent.agent_type,
            position=(i, j),
            capital=initial_capital,
            utility=self.utility(initial_capital, property_price),
        )

    def get_real_state_agent(self, i: int, j: int) -> RealStateAgent:
        return typing_cast(RealStateAgent, self.get_agent(i, j))

    def property_price(self, similar_amount: int) -> float:
        return self.__price_formula.apply(similar_amount)

    def utility(self, capital: float, price: float) -> float:
        return self.__utility_formula.apply(capital, price)

    def step(
        self,
        i: int,
        j: int,
        configuration: Lattice,
    ) -> None:
        position_1, position_2 = self._random_positions_to_swap()
        agent_1 = self.get_real_state_agent(*position_1)
        agent_2 = self.get_real_state_agent(*position_2)
        agent_1.try_sale_against(counterparty=agent_2, model=self, configuration=configuration)

    def utility_of(self, i: int, j: int) -> float:
        agent = self.get_real_state_agent(i, j)
        return agent.utility

    def updated_utility_of(self, i: int, j: int) -> float:
        agent = self.get_real_state_agent(i, j)
        similar_amount = self.similar_neighbors_amount(i, j, count_myself=True)
        property_price = self.property_price(similar_amount)
        return self.utility(agent.capital, property_price)

    @as_series
    def agent_types_lattice(self) -> List[List[int]]:
        action = lambda i, j: int(self.get_real_state_agent(i, j).agent_type)
        return self._process_lattice_with(action)

    @as_series
    def utility_level_lattice(self, flatten: bool = False) -> List[List[float]]:
        return self._process_lattice_with(self.utility_of, flatten=flatten)

    @as_series
    def updated_utility_level_lattice(self, flatten: bool = False) -> List[List[float]]:
        return self._process_lattice_with(self.updated_utility_of, flatten=flatten)

    @as_series
    def capital_level_lattice(self, flatten: bool = False) -> List[List[float]]:
        action = lambda i, j: self.get_real_state_agent(i, j).capital
        return self._process_lattice_with(action, flatten=flatten)

    @as_series
    def capital_level_and_agent_type_lattice(
        self, flatten: bool = False
    ) -> List[List[Tuple[float, int]]]:
        action = lambda i, j: (
            self.get_real_state_agent(i, j).capital,
            self.get_real_state_agent(i, j).agent_type,
        )
        return self._process_lattice_with(action, flatten=flatten)

    @as_series_with(metadata={"states": ["satisfied", "dissatisfied"]})
    def dissatisfaction_threshold_lattice(self) -> List[List[int]]:
        action = lambda i, j: (
            self.get_real_state_agent(i, j).agent_type + self.agent_types
            if self.utility_of(i, j) < self.utility_tolerance
            else self.get_real_state_agent(i, j).agent_type
        )
        return self._process_lattice_with(action)

    @as_series_with(depends=("utility_level_lattice",))
    def total_average_utility_level(self) -> float:
        total_utilities = self._flatten("utility_level_lattice")
        return sum(total_utilities) / self.length**2

    @as_series_with(depends=("updated_utility_level_lattice",))
    def total_average_updated_utility_level(self) -> float:
        total_utilities = self._flatten("updated_utility_level_lattice")
        return sum(total_utilities) / self.length**2

    @as_series_with(depends=("capital_level_lattice",))
    def total_average_capital_level(self) -> float:
        total_capitals = self._flatten("capital_level_lattice")
        return sum(total_capitals) / self.length**2
