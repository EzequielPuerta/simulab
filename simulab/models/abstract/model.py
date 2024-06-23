from abc import ABC, abstractmethod
from copy import deepcopy
from functools import partial
from typing import Any, Callable, Dict, List, Set, Tuple, Type, Union

import networkx as nx
import numpy as np

from simulab.models.abstract.agent import Agent
from simulab.simulation.core.equilibrium_criterion import AbstractCriterion
from simulab.simulation.core.lattice import Lattice
from simulab.simulation.core.neighborhood import Neighborhood, VonNeumann


class AbstractLatticeModel(ABC):
    def __init__(
        self,
        length: int,
        configuration: Lattice | np.ndarray | None = None,
        neighborhood: Type[Neighborhood] = VonNeumann,
        agent_types: int = 2,
        update_simultaneously: bool = False,
        update_sorted_by_agent_type: bool = False,
    ):
        self.length = length
        self.neighborhood = neighborhood(self.length)
        self.agent_types = agent_types
        self.update_simultaneously = update_simultaneously
        self.update_sorted_by_agent_type = update_sorted_by_agent_type
        self.series_history: Dict[str, List[List[Union[int, float]]]] = {}
        self.__initial_configuration = configuration

    def __initialize(self) -> None:
        self._by_type: Dict[int, Set[Tuple[int, int]]] = {
            _type: set() for _type in range(self.agent_types)
        }
        self.__configure_agents()
        self.__configure_series()

    def __configure_agents(self) -> None:
        raw = deepcopy(self.__initial_configuration)
        if isinstance(raw, Lattice):
            pass
        elif raw is not None:
            raw = Lattice(raw)
        else:
            raw = Lattice.random(self.agent_types, self.length)
        self.configuration = raw

        try:
            for method in [self.__basic_agent, self._create_agent]:
                self._process_lattice_with(
                    partial(self.__create_agent_as, method),
                    inplace=True,
                )
        except NotImplementedError:
            pass

    def __create_agent_as(
        self,
        method: Callable[[int, int, int], Agent],
        i: int,
        j: int,
    ) -> Agent:
        agent = method(self.configuration.at(i, j), i, j)
        self._by_type[agent.agent_type].add((i, j))
        return agent

    def __basic_agent(self, agent_type: int, i: int, j: int) -> Agent:
        return Agent(agent_type=agent_type)

    def _create_agent(self, basic_agent: Agent, i: int, j: int) -> Agent:
        # Overload this method in your model to create custom agents based on
        # basic agents previously created, in the (i,j) position of the
        # configuration lattice, replacing the older basic model.
        raise NotImplementedError

    def _process_lattice_with(
        self,
        action: Callable[[int, int], Any],
        inplace: bool = False,
        flatten: bool = False,
    ) -> List[List[Any]]:
        return self.configuration.process_with(  # type: ignore[return-value]
            action,
            inplace=inplace,
            flatten=flatten,
        )

    ROOT = "ROOT"

    def __configure_series(self) -> None:
        self.series: Dict[str, Any] = {}
        self.__dependencies__ = nx.DiGraph()
        self.__dependencies__.add_node(self.ROOT)
        for method_name in dir(self):
            method = getattr(self, method_name)
            try:
                if method.__is_series__:
                    self.series[method.__name__] = []
                    if method.__depends__:
                        for dependency in method.__depends__:
                            self.__dependencies__.add_edge(method.__name__, dependency)
                    else:
                        self.__dependencies__.add_edge(method.__name__, self.ROOT)
            except AttributeError:
                pass
        bfs_edges = list(nx.bfs_edges(self.__dependencies__, self.ROOT, reverse=True))
        self._sorted_series_names = [series_name for dependency, series_name in bfs_edges]

    def __take_snapshot(self) -> None:
        for name in self._sorted_series_names:
            self.series[name].append(getattr(self, name)())

    def __save_series_history(self, series: Tuple[str]) -> None:
        if len(series) > 0:
            for name in series:
                try:
                    history = self.series_history[name]
                except KeyError:
                    self.series_history[name] = []
                    history = self.series_history[name]
                finally:
                    try:
                        history.append(self.series[name])
                    except KeyError:
                        raise ValueError(f"There is no series named as '{name}'.")

    def _random_positions_to_swap(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        return (
            tuple(position)  # type: ignore[return-value]
            for position in np.random.randint(0, self.length, size=(2, 2))
        )

    def get_agent(self, i: int, j: int) -> Agent:
        return self.configuration.at(i, j)

    def similar_neighbors_amount(
        self,
        i: int,
        j: int,
        agent_type: int | None = None,
        count_myself: bool = False,
    ) -> int:
        _agent_type = agent_type if agent_type else self.get_agent(i, j).agent_type
        like_minded_neighbors = [
            1
            for row, col in self.neighborhood.indexes_for(i, j)
            if self.get_agent(row, col).agent_type == _agent_type
        ]
        total = sum(like_minded_neighbors)
        return total + 1 if count_myself else total

    def run_with(
        self,
        max_steps: int,
        criterion: AbstractCriterion,
        saving_series: Tuple[str],
    ) -> None:
        self.__initialize()
        self.__take_snapshot()
        for _ in range(max_steps):
            self.run_step()
            self.__take_snapshot()
            if criterion.in_equilibrium(self.series):
                break
        self.__save_series_history(series=saving_series)

    def run_step(self) -> None:
        configuration = (
            deepcopy(self.configuration) if self.update_simultaneously else self.configuration
        )
        if self.update_sorted_by_agent_type:
            for _type in range(self.agent_types):
                for position in self._by_type[_type]:
                    self.step(*position, configuration=configuration)
        else:
            for i, j in ((i, j) for i in range(self.length) for j in range(self.length)):
                self.step(i, j, configuration=configuration)
        if self.update_simultaneously:
            self.configuration = configuration

    @abstractmethod
    def step(
        self,
        i: int,
        j: int,
        configuration: Lattice,
    ) -> None:
        pass

    def _flatten(self, series_name: str) -> List[Any]:
        return sum(self.series[series_name][-1], [])


def __as_series(
    model_function: Callable[[Any], Any],
    depends: Tuple[str] | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Callable[[Any], Any]:
    model_function.__is_series__ = True  # type: ignore[attr-defined]
    model_function.__depends__ = depends  # type: ignore[attr-defined]
    model_function.__series_metadata__ = metadata if metadata else {}  # type: ignore[attr-defined]
    return model_function


def as_series(model_function: Callable[[Any], Any]) -> Callable[[Any], Any]:
    return __as_series(model_function)


def as_series_with(
    depends: Tuple[str] | None = None,
    metadata: Dict[str, Any] | None = None,
) -> Callable[[Any], Any]:
    def decorator(model_function: Callable[[Any], Any]) -> Callable[[Any], Any]:
        return __as_series(model_function, depends, metadata)

    return decorator
