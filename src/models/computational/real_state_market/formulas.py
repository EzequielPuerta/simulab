class UtilityFormula:
    def __init__(self, alpha: float) -> None:
        self.alpha = alpha

    def apply(self, capital: float, price: float) -> float:
        return (capital ** (self.alpha)) * (price ** (1 - self.alpha))


class PriceFormula:
    def __init__(self, A: float, B: float, neighborhood_size: int) -> None:
        self.A = A
        self.B = B
        self.neighborhood_size = neighborhood_size

    def apply(self, similar_neighbors_amount: int) -> float:
        distinct_amount = self.neighborhood_size - similar_neighbors_amount + 1
        return self.A * (similar_neighbors_amount - distinct_amount) + self.B
