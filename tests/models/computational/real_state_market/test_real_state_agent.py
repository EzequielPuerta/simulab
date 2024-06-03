from typing import Tuple

import numpy as np
import pytest

from simulab.models.computational.real_state_market.agent import RealStateAgent, Transaction, Transfer
from simulab.models.computational.real_state_market.formulas import PriceFormula, UtilityFormula
from simulab.simulation.core.lattice import Lattice
from simulab.simulation.core.neighborhood import Moore


class MockRealStateModel:
    __utility_formula = UtilityFormula(0.5)
    __price_formula = PriceFormula(1 / 16, 0.5, Moore.size())

    def _mock_similar_neighbors_amount(
        self,
        payer_position: Tuple[int, int],
        seller_position: Tuple[int, int],
        payer_similar_amount_in_target: int,
        seller_similar_amount_in_target: int,
    ) -> None:
        def __similar_neighbors_amount_in_target(  # type: ignore[no-untyped-def]
            *position: Tuple[int, int],
            **kwargs,
        ) -> int:
            if position == payer_position:
                return seller_similar_amount_in_target
            elif position == seller_position:
                return payer_similar_amount_in_target
            else:
                raise ValueError

        self.similar_neighbors_amount = __similar_neighbors_amount_in_target

    def property_price(self, similar_amount: int) -> float:
        return self.__price_formula.apply(similar_amount)

    def utility(self, capital: float, price: float) -> float:
        return self.__utility_formula.apply(capital, price)


@pytest.fixture
def lattice() -> Lattice:  # type: ignore[misc]
    configuration = np.array([[1, 0, 1, 1], [1, 0, 0, 1], [1, 0, 1, 1], [0, 0, 0, 0]])
    yield Lattice(configuration)


@pytest.fixture
def mock_model() -> MockRealStateModel:  # type: ignore[misc]
    yield MockRealStateModel()


def test_real_state_agent_creation() -> None:
    real_state_agent = RealStateAgent(0, (1, 1), 1.0, 1.0)
    assert real_state_agent.agent_type == 0
    assert real_state_agent.position == (1, 1)
    assert real_state_agent.utility == 1.0
    assert real_state_agent.capital == 1.0


def test_transfer_is_not_convenient(mock_model, lattice) -> None:  # type: ignore[no-untyped-def]
    capital = 1.0

    payer_type = 0
    payer_position = (3, 1)
    payer_similar_amount_in_origin = 5
    payer_similar_amount_in_target = 4
    payer_utility = mock_model.utility(
        capital,
        mock_model.property_price(payer_similar_amount_in_origin),
    )
    seller_type = 1
    seller_position = (1, 0)
    seller_similar_amount_in_origin = 6
    seller_similar_amount_in_target = 5
    seller_utility = mock_model.utility(
        capital,
        mock_model.property_price(seller_similar_amount_in_origin),
    )

    payer = RealStateAgent(
        payer_type,
        payer_position,
        payer_utility,
        capital,
    )
    seller = RealStateAgent(
        seller_type,
        seller_position,
        seller_utility,
        capital,
    )
    lattice.set(*payer_position, _with=payer)
    lattice.set(*seller_position, _with=seller)

    to_pay = mock_model.property_price(payer_similar_amount_in_target)
    to_charge = mock_model.property_price(seller_similar_amount_in_target)
    average = (to_pay + to_charge) / 2
    assert to_pay - average < payer.capital
    assert to_charge - average < seller.capital

    payer_transfer = Transfer(payer, to_pay, seller, to_charge, average, mock_model)
    seller_transfer = Transfer(seller, to_charge, payer, to_pay, average, mock_model)
    assert not payer_transfer.is_convenient and not seller_transfer.is_convenient
    assert lattice.at(*payer_position) == payer
    assert lattice.at(*seller_position) == seller
    assert payer.position == payer_position
    assert payer.agent_type == payer_type
    assert payer.capital == capital
    assert payer.utility == payer_utility
    assert seller.position == seller_position
    assert seller.agent_type == seller_type
    assert seller.capital == capital
    assert seller.utility == seller_utility


def test_transfer_is_convenient(mock_model, lattice) -> None:  # type: ignore[no-untyped-def]
    capital = 1.0

    payer_type = 0
    payer_position = (1, 1)
    payer_similar_amount_in_origin = 4
    payer_similar_amount_in_target = 6
    payer_utility = mock_model.utility(
        capital,
        mock_model.property_price(payer_similar_amount_in_origin),
    )
    seller_type = 1
    seller_position = (2, 2)
    seller_similar_amount_in_origin = 3
    seller_similar_amount_in_target = 5
    seller_utility = mock_model.utility(
        capital,
        mock_model.property_price(seller_similar_amount_in_origin),
    )

    payer = RealStateAgent(
        payer_type,
        payer_position,
        payer_utility,
        capital,
    )
    seller = RealStateAgent(
        seller_type,
        seller_position,
        seller_utility,
        capital,
    )
    lattice.set(*payer_position, _with=payer)
    lattice.set(*seller_position, _with=seller)

    to_pay = mock_model.property_price(payer_similar_amount_in_target)
    to_charge = mock_model.property_price(seller_similar_amount_in_target)
    average = (to_pay + to_charge) / 2
    assert to_pay - average < payer.capital
    assert to_charge - average < seller.capital

    payer_transfer = Transfer(payer, to_pay, seller, to_charge, average, mock_model)
    seller_transfer = Transfer(seller, to_charge, payer, to_pay, average, mock_model)
    assert payer_transfer.is_convenient and seller_transfer.is_convenient
    assert lattice.at(*payer_position) == payer
    assert lattice.at(*seller_position) == seller
    assert payer.position == payer_position
    assert seller.position == seller_position
    payer_transfer.apply(lattice)
    seller_transfer.apply(lattice)
    assert lattice.at(*payer_position) == seller
    assert lattice.at(*seller_position) == payer
    assert payer.position == seller_position
    assert payer.agent_type == payer_type
    assert payer.capital == capital + to_charge - average
    assert payer.utility == mock_model.utility(payer.capital, to_pay)
    assert seller.position == payer_position
    assert seller.agent_type == seller_type
    assert seller.capital == capital + to_pay - average
    assert seller.utility == mock_model.utility(seller.capital, to_charge)


def test_not_convenient_transaction(mock_model, lattice) -> None:  # type: ignore[no-untyped-def]
    capital = 1.0

    payer_type = 0
    payer_position = (3, 1)
    payer_similar_amount_in_origin = 5
    payer_similar_amount_in_target = 4
    payer_utility = mock_model.utility(
        capital,
        mock_model.property_price(payer_similar_amount_in_origin),
    )
    seller_type = 1
    seller_position = (1, 0)
    seller_similar_amount_in_origin = 6
    seller_similar_amount_in_target = 5
    seller_utility = mock_model.utility(
        capital,
        mock_model.property_price(seller_similar_amount_in_origin),
    )
    mock_model._mock_similar_neighbors_amount(
        payer_position,
        seller_position,
        payer_similar_amount_in_target,
        seller_similar_amount_in_target,
    )

    payer = RealStateAgent(
        payer_type,
        payer_position,
        payer_utility,
        capital,
    )
    seller = RealStateAgent(
        seller_type,
        seller_position,
        seller_utility,
        capital,
    )
    lattice.set(*payer_position, _with=payer)
    lattice.set(*seller_position, _with=seller)
    assert lattice.at(*payer_position) == payer
    assert lattice.at(*seller_position) == seller
    assert payer.position == payer_position
    assert seller.position == seller_position

    Transaction(
        between=payer,
        _and=seller,
        model=mock_model,
        configuration=lattice,
    )

    assert lattice.at(*payer_position) == payer
    assert lattice.at(*seller_position) == seller
    assert payer.position == payer_position
    assert payer.agent_type == payer_type
    assert payer.capital == capital
    assert payer.utility == payer_utility
    assert seller.position == seller_position
    assert seller.agent_type == seller_type
    assert seller.capital == capital
    assert seller.utility == seller_utility


def test_convenient_transaction(mock_model, lattice) -> None:  # type: ignore[no-untyped-def]
    capital = 1.0

    payer_type = 0
    payer_position = (1, 1)
    payer_similar_amount_in_origin = 4
    payer_similar_amount_in_target = 6
    payer_utility = mock_model.utility(
        capital,
        mock_model.property_price(payer_similar_amount_in_origin),
    )
    seller_type = 1
    seller_position = (2, 2)
    seller_similar_amount_in_origin = 3
    seller_similar_amount_in_target = 5
    seller_utility = mock_model.utility(
        capital,
        mock_model.property_price(seller_similar_amount_in_origin),
    )
    mock_model._mock_similar_neighbors_amount(
        payer_position,
        seller_position,
        payer_similar_amount_in_target,
        seller_similar_amount_in_target,
    )

    payer = RealStateAgent(
        payer_type,
        payer_position,
        payer_utility,
        capital,
    )
    seller = RealStateAgent(
        seller_type,
        seller_position,
        seller_utility,
        capital,
    )
    lattice.set(*payer_position, _with=payer)
    lattice.set(*seller_position, _with=seller)
    assert lattice.at(*payer_position) == payer
    assert lattice.at(*seller_position) == seller
    assert payer.position == payer_position
    assert seller.position == seller_position

    to_pay = mock_model.property_price(payer_similar_amount_in_target)
    to_charge = mock_model.property_price(seller_similar_amount_in_target)
    average = (to_pay + to_charge) / 2

    Transaction(
        between=payer,
        _and=seller,
        model=mock_model,
        configuration=lattice,
    )

    assert lattice.at(*payer_position) == seller
    assert lattice.at(*seller_position) == payer
    assert payer.position == seller_position
    assert payer.agent_type == payer_type
    assert payer.capital == capital + to_charge - average
    assert payer.utility == mock_model.utility(payer.capital, to_pay)
    assert seller.position == payer_position
    assert seller.agent_type == seller_type
    assert seller.capital == capital + to_pay - average
    assert seller.utility == mock_model.utility(seller.capital, to_charge)


def test_not_effective_sale(mock_model, lattice) -> None:  # type: ignore[no-untyped-def]
    capital = 1.0

    payer_type = 0
    payer_position = (3, 1)
    payer_similar_amount_in_origin = 5
    payer_similar_amount_in_target = 4
    payer_utility = mock_model.utility(
        capital,
        mock_model.property_price(payer_similar_amount_in_origin),
    )
    seller_type = 1
    seller_position = (1, 0)
    seller_similar_amount_in_origin = 6
    seller_similar_amount_in_target = 5
    seller_utility = mock_model.utility(
        capital,
        mock_model.property_price(seller_similar_amount_in_origin),
    )
    mock_model._mock_similar_neighbors_amount(
        payer_position,
        seller_position,
        payer_similar_amount_in_target,
        seller_similar_amount_in_target,
    )

    payer = RealStateAgent(
        payer_type,
        payer_position,
        payer_utility,
        capital,
    )
    seller = RealStateAgent(
        seller_type,
        seller_position,
        seller_utility,
        capital,
    )
    lattice.set(*payer_position, _with=payer)
    lattice.set(*seller_position, _with=seller)
    assert lattice.at(*payer_position) == payer
    assert lattice.at(*seller_position) == seller
    assert payer.position == payer_position
    assert seller.position == seller_position

    payer.try_sale_against(
        counterparty=seller,
        model=mock_model,
        configuration=lattice,
    )

    assert lattice.at(*payer_position) == payer
    assert lattice.at(*seller_position) == seller
    assert payer.position == payer_position
    assert payer.agent_type == payer_type
    assert payer.capital == capital
    assert payer.utility == payer_utility
    assert seller.position == seller_position
    assert seller.agent_type == seller_type
    assert seller.capital == capital
    assert seller.utility == seller_utility


def test_effective_sale(mock_model, lattice) -> None:  # type: ignore[no-untyped-def]
    capital = 1.0

    payer_type = 0
    payer_position = (1, 1)
    payer_similar_amount_in_origin = 4
    payer_similar_amount_in_target = 6
    payer_utility = mock_model.utility(
        capital,
        mock_model.property_price(payer_similar_amount_in_origin),
    )
    seller_type = 1
    seller_position = (2, 2)
    seller_similar_amount_in_origin = 3
    seller_similar_amount_in_target = 5
    seller_utility = mock_model.utility(
        capital,
        mock_model.property_price(seller_similar_amount_in_origin),
    )
    mock_model._mock_similar_neighbors_amount(
        payer_position,
        seller_position,
        payer_similar_amount_in_target,
        seller_similar_amount_in_target,
    )

    payer = RealStateAgent(
        payer_type,
        payer_position,
        payer_utility,
        capital,
    )
    seller = RealStateAgent(
        seller_type,
        seller_position,
        seller_utility,
        capital,
    )
    lattice.set(*payer_position, _with=payer)
    lattice.set(*seller_position, _with=seller)
    assert lattice.at(*payer_position) == payer
    assert lattice.at(*seller_position) == seller
    assert payer.position == payer_position
    assert seller.position == seller_position

    to_pay = mock_model.property_price(payer_similar_amount_in_target)
    to_charge = mock_model.property_price(seller_similar_amount_in_target)
    average = (to_pay + to_charge) / 2

    payer.try_sale_against(
        counterparty=seller,
        model=mock_model,
        configuration=lattice,
    )

    assert lattice.at(*payer_position) == seller
    assert lattice.at(*seller_position) == payer
    assert payer.position == seller_position
    assert payer.agent_type == payer_type
    assert payer.capital == capital + to_charge - average
    assert payer.utility == mock_model.utility(payer.capital, to_pay)
    assert seller.position == payer_position
    assert seller.agent_type == seller_type
    assert seller.capital == capital + to_pay - average
    assert seller.utility == mock_model.utility(seller.capital, to_charge)
