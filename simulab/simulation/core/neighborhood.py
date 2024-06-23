from abc import ABC, abstractmethod
from functools import partial, partialmethod
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


def _size(vision_range: int) -> int:
    side = 2 * vision_range + 1
    return side * side - 1


def _indexes_at_range(  # type: ignore[no-untyped-def]
    self,
    vision_range: int,
    i: int,
    j: int = 0,
) -> List[Tuple[int, int]]:
    start_i = i - vision_range
    start_j = j - vision_range
    end_i = i + vision_range
    end_j = j + vision_range

    return [
        (self._norm(x), self._norm(y))
        for x in range(start_i, end_i + 1)
        for y in range(start_j, end_j + 1)
        if (x, y) != (i, j)
    ]


class ExpandedMoore:
    def __new__(self, vision_range: int):  # type: ignore[no-untyped-def]
        assert vision_range > 0, "Vision range should be greater than 0"
        WrappedExpandedMoore = type(
            "WrappedExpandedMoore",
            (Neighborhood,),
            {
                "size": partial(_size, vision_range),
                "indexes_for": partialmethod(_indexes_at_range, vision_range),
            },
        )
        return WrappedExpandedMoore
