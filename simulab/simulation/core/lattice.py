from typing import Any, Callable, List

import numpy as np


class Lattice:
    def __init__(
        self,
        configuration: np.ndarray | List,  # type: ignore[type-arg]
    ) -> None:
        self.update_with(configuration)
        self.length = len(self.configuration)

    def update_with(self, configuration: np.ndarray | List) -> None:  # type: ignore[type-arg]
        self.configuration = (
            configuration.tolist() if isinstance(configuration, np.ndarray) else configuration
        )

    def __repr__(self) -> str:
        representation = str(self.configuration[0])
        for row in self.configuration[1:]:
            representation = representation + "\n" + str(row)
        return representation

    @classmethod
    def full(cls, fill_value: int, length: int) -> "Lattice":
        return cls(np.full((length, length), fill_value))

    @classmethod
    def zeros(cls, length: int) -> "Lattice":
        return cls(np.zeros((length, length)))

    @classmethod
    def ones(cls, length: int) -> "Lattice":
        return cls(np.ones((length, length)))

    @classmethod
    def random(cls, value: int, length: int) -> "Lattice":
        return cls(np.random.randint(value, size=(length, length)))

    @classmethod
    def with_probability(cls, probability: float, length: int) -> "Lattice":
        ones = int(length * length * probability)
        zeros = length * length - ones
        result = np.array([0] * zeros + [1] * ones)
        np.random.shuffle(result)
        return cls(result.reshape((length, length)))

    def at(self, i: int, j: int) -> Any:
        return self.configuration[i][j]

    def set(self, i: int, j: int, _with: Any) -> None:
        self.configuration[i][j] = _with

    def process_with(
        self,
        action: Callable[[int, int], Any],
        inplace: bool = False,
        flatten: bool = False,
    ) -> List[List[Any]] | None:
        if inplace:
            for i in range(self.length):
                for j in range(self.length):
                    self.set(i, j, action(i, j))
            return None
        else:
            result = [[action(i, j) for j in range(self.length)] for i in range(self.length)]
            return sum(result, []) if flatten else result
