from simulab.models.computational.real_state_market.formulas import PriceFormula, UtilityFormula


def test_utility_formula() -> None:
    utility = UtilityFormula(0.5)
    assert utility.alpha == 0.5
    assert utility.apply(1.0, 0.25) == 0.5


def test_price_formula() -> None:
    price = PriceFormula(1 / 16, 0.5, 8)
    assert price.A == 1 / 16
    assert price.B == 0.5
    assert price.neighborhood_size == 8
    assert price.apply(3) == 0.3125
