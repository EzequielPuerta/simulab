from abc import ABC, abstractmethod
from typing import Any, Dict

import numpy as np


class AbstractCriterion(ABC):
    @abstractmethod
    def in_equilibrium(self, series: Dict[str, Any]) -> bool:
        pass


class WithoutCriterion(AbstractCriterion):
    def in_equilibrium(self, series: Dict[str, Any]) -> bool:
        return False


class EquilibriumCriterion(AbstractCriterion):
    def __init__(
        self,
        series_name: str,
        window_size: int = 20,
        tolerance: float = 0.001,
    ):
        self.series_name: str = series_name
        self.window_size: int = window_size
        self.tolerance: float = tolerance

    def in_equilibrium(self, series: Dict[str, Any]) -> bool:
        try:
            _series = series[self.series_name]
        except KeyError:
            raise AssertionError(f"There is no series called '{self.series_name}'.")
        else:
            length = len(_series)
            if length <= self.window_size:
                return False
            else:
                window = range(length - self.window_size, length)
                return all(
                    (
                        np.abs((_series[i] - _series[i - 1]) / _series[i - 1]) < self.tolerance
                        for i in window
                    )
                )
