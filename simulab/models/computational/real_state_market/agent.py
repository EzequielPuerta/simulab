from typing import Tuple

from simulab.models.abstract.agent import Agent
from simulab.models.abstract.model import AbstractLatticeModel
from simulab.simulation.core.lattice import Lattice


class Transfer:
    def __init__(
        self,
        payer: "RealStateAgent",
        to_pay: float,
        seller: "RealStateAgent",
        to_charge: float,
        average: float,
        model: AbstractLatticeModel,
    ) -> None:
        self.payer = payer
        self.price_to_pay = to_pay
        self.seller = seller
        self.price_to_charge = to_charge
        self.average = average
        self.is_convenient = False
        self.__original_seller_position = seller.position
        self.__on(model)

    def __on(self, model: AbstractLatticeModel) -> None:
        self.new_capital = self.payer.capital + self.price_to_charge - self.average
        self.new_utility = model.utility(  # type: ignore[attr-defined]
            self.new_capital,
            self.price_to_pay,
        )
        self.is_convenient = self.new_utility > self.payer.utility

    def apply(self, configuration: Lattice) -> None:
        self.payer.capital = self.new_capital
        self.payer.utility = self.new_utility
        self.payer.position = self.__original_seller_position
        configuration.set(*self.__original_seller_position, _with=self.payer)


class Transaction:
    def __init__(
        self,
        between: "RealStateAgent",
        _and: "RealStateAgent",
        model: AbstractLatticeModel,
        configuration: Lattice,
    ) -> None:
        self.agent_A = between
        self.agent_B = _and
        self.payment_A = self.agent_A._target_price(model, self.agent_B)
        self.payment_B = self.agent_B._target_price(model, self.agent_A)
        self.average = (self.payment_A + self.payment_B) / 2
        enough_capital_A = self.payment_A - self.average < self.agent_A.capital
        enough_capital_B = self.payment_B - self.average < self.agent_B.capital
        if enough_capital_A and enough_capital_B:
            transfer_A = self.__transfer(_from="A", _to="B", model=model)
            transfer_B = self.__transfer(_from="B", _to="A", model=model)
            if transfer_A.is_convenient and transfer_B.is_convenient:
                transfer_A.apply(configuration)
                transfer_B.apply(configuration)

    def __transfer(
        self,
        _from: str,
        _to: str,
        model: AbstractLatticeModel,
    ) -> Transfer:
        return Transfer(
            getattr(self, f"agent_{_from}"),
            getattr(self, f"payment_{_from}"),
            getattr(self, f"agent_{_to}"),
            getattr(self, f"payment_{_to}"),
            self.average,
            model,
        )


class RealStateAgent(Agent):
    def __init__(
        self,
        agent_type: int,
        position: Tuple[int, int],
        utility: float,
        capital: float = 1.0,
    ):
        super(RealStateAgent, self).__init__(agent_type)
        self.position = position
        self.utility = utility
        self.capital = capital

    def try_sale_against(
        self,
        counterparty: "RealStateAgent",
        model: AbstractLatticeModel,
        configuration: Lattice,
    ) -> None:
        Transaction(between=self, _and=counterparty, model=model, configuration=configuration)

    def _target_price(
        self,
        model: AbstractLatticeModel,
        agent: "RealStateAgent",
    ) -> float:
        target_similar_amount = model.similar_neighbors_amount(
            *agent.position, agent_type=self.agent_type, count_myself=True
        )
        return model.property_price(target_similar_amount)  # type: ignore[attr-defined]
