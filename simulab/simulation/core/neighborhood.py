from abc import ABC, abstractmethod
from typing import List, Tuple


class Neighborhood(ABC):
    def __init__(self, world_size: int):
        self._world_size = world_size

    @classmethod
    @abstractmethod
    def size(cls) -> int:
        pass

    def _norm(self, index: int) -> int:
        return index % self._world_size

    @abstractmethod
    def indexes_for(self, i: int, j: int) -> List[Tuple[int, int]]:
        pass


class Immediate(Neighborhood):
    @classmethod
    def size(cls) -> int:
        return 2

    def indexes_for(self, i: int, j: int) -> List[Tuple[int, int]]:
        return [(self._norm(x), self._norm(y)) for x, y in [(i, j - 1), (i, j + 1)]]


class VonNeumann(Neighborhood):
    @classmethod
    def size(cls) -> int:
        return 4

    def indexes_for(self, i: int, j: int) -> List[Tuple[int, int]]:
        return [
            (self._norm(x), self._norm(y))
            for x, y in [(i, j - 1), (i, j + 1), (i - 1, j), (i + 1, j)]
        ]


class Moore(Neighborhood):
    @classmethod
    def size(cls) -> int:
        return 8

    def indexes_for(self, i: int, j: int) -> List[Tuple[int, int]]:
        return [
            (self._norm(x), self._norm(y))
            for x, y in [
                (i, j - 1),
                (i, j + 1),
                (i - 1, j),
                (i + 1, j),
                (i + 1, j - 1),
                (i + 1, j + 1),
                (i - 1, j - 1),
                (i - 1, j + 1),
            ]
        ]
