from abc import ABC, abstractmethod

import numpy as np

from simulab.simulation.core.lattice import Lattice


class Seed(ABC):
    def __init__(self, i: int, j: int) -> None:
        self.i = i
        self.j = j

    def apply_on(self, lattice: Lattice) -> None:
        temp = np.array(lattice.configuration)
        self._apply_on(temp)
        lattice.update_with(temp)

    @abstractmethod
    def _apply_on(self, configuration: np.ndarray) -> None:
        pass

    def __str__(self) -> str:
        return f"{type(self).__name__}({self.i},{self.j})"

    def __repr__(self) -> str:
        return str(self)


# Still lifes
class Block(Seed):
    def _apply_on(self, configuration: np.ndarray) -> None:
        block = np.array([[1, 1], [1, 1]])
        configuration[self.i : self.i + 2, self.j : self.j + 2] = block


class BeeHive(Seed):
    def _apply_on(self, configuration: np.ndarray) -> None:
        bee_hive = np.array([[0, 1, 1, 0], [1, 0, 0, 1], [0, 1, 1, 0]])
        configuration[self.i : self.i + 3, self.j : self.j + 4] = bee_hive


class Loaf(Seed):
    def _apply_on(self, configuration: np.ndarray) -> None:
        loaf = np.array([[0, 1, 1, 0], [1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 0]])
        configuration[self.i : self.i + 4, self.j : self.j + 4] = loaf


class Boat(Seed):
    def _apply_on(self, configuration: np.ndarray) -> None:
        boat = np.array([[1, 1, 0], [1, 0, 1], [0, 1, 0]])
        configuration[self.i : self.i + 3, self.j : self.j + 3] = boat


class Tub(Seed):
    def _apply_on(self, configuration: np.ndarray) -> None:
        tub = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
        configuration[self.i : self.i + 3, self.j : self.j + 3] = tub


# Oscilators
class Blinker(Seed):
    def _apply_on(self, configuration: np.ndarray) -> None:
        blinker = np.array([[1, 1, 1]])
        configuration[self.i : self.i + 3, self.j] = blinker


class Toad(Seed):
    def _apply_on(self, configuration: np.ndarray) -> None:
        toad = np.array([[0, 1, 1, 1], [1, 1, 1, 0]])
        configuration[self.i : self.i + 2, self.j : self.j + 4] = toad


class Beacon(Seed):
    def _apply_on(self, configuration: np.ndarray) -> None:
        beacon = np.array([[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 1, 1], [0, 0, 1, 1]])
        configuration[self.i : self.i + 4, self.j : self.j + 4] = beacon


class Pulsar(Seed):
    def _apply_on(self, configuration: np.ndarray) -> None:
        pulsar = np.array(
            [
                [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
                [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0],
            ]
        )
        configuration[self.i : self.i + 13, self.j : self.j + 13] = pulsar


class Pentadecathlon(Seed):
    def _apply_on(self, configuration: np.ndarray) -> None:
        pentadecathlon = np.array(
            [
                [0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
                [1, 1, 0, 1, 1, 1, 1, 0, 1, 1],
                [0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
            ]
        )
        configuration[self.i : self.i + 3, self.j : self.j + 10] = pentadecathlon


# Spaceships
class Glider(Seed):
    def _apply_on(self, configuration: np.ndarray) -> None:
        glider = np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]])
        configuration[self.i : self.i + 3, self.j : self.j + 3] = glider


class LightWeightSpaceship(Seed):
    def _apply_on(self, configuration: np.ndarray) -> None:
        lwss = np.array([[0, 1, 0, 0, 1], [1, 0, 0, 0, 0], [1, 0, 0, 0, 1], [1, 1, 1, 1, 0]])
        configuration[self.i : self.i + 4, self.j : self.j + 5] = lwss


class MiddleWeightSpaceship(Seed):
    def _apply_on(self, configuration: np.ndarray) -> None:
        mwss = np.array(
            [
                [0, 0, 0, 1, 0, 0],
                [0, 1, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 1],
                [1, 1, 1, 1, 1, 0],
            ]
        )
        configuration[self.i : self.i + 5, self.j : self.j + 6] = mwss


class HeavyWeightSpaceship(Seed):
    def _apply_on(self, configuration: np.ndarray) -> None:
        hwss = np.array(
            [
                [0, 0, 0, 1, 1, 0, 0],
                [0, 1, 0, 0, 0, 0, 1],
                [1, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 0, 0, 0, 1],
                [1, 1, 1, 1, 1, 1, 0],
            ]
        )
        configuration[self.i : self.i + 5, self.j : self.j + 7] = hwss
