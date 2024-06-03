from typing import List, cast

import networkx as nx

from simulab.models.abstract.model import AbstractLatticeModel, as_series
from simulab.simulation.core.lattice import Lattice


class Condensation(AbstractLatticeModel):
    CONDENSES = 1
    EVAPORATES = 0

    def __init__(  # type: ignore[no-untyped-def]
        self,
        probability: float,
        *args,
        **kwargs,
    ):
        self.probability: float = probability
        length = kwargs.get("length")
        configuration = kwargs.get(
            "configuration", Lattice.with_probability(self.probability, cast(int, length))
        )
        super(Condensation, self).__init__(  # type: ignore[misc]
            *args,
            update_simultaneously=True,
            configuration=configuration,
            **kwargs,
        )

    def __condensed_amount(self, i: int, j: int) -> int:
        return self.similar_neighbors_amount(i, j, agent_type=1)

    def step(
        self,
        i: int,
        j: int,
        configuration: Lattice,
    ) -> None:
        agent_type = self.get_agent(i, j).agent_type
        neighbors = self.__condensed_amount(i, j) + agent_type
        if agent_type == self.EVAPORATES and neighbors >= 4:
            configuration.at(i, j).agent_type = self.CONDENSES
        if agent_type == self.CONDENSES and neighbors < 4:
            configuration.at(i, j).agent_type = self.EVAPORATES

    @as_series
    def agent_types_lattice(self) -> List[List[int]]:
        action = lambda i, j: int(self.get_agent(i, j).agent_type)
        return self._process_lattice_with(action)

    @as_series
    def maximum_cluster_size(self) -> int:
        graph = nx.Graph()
        add_nodes = lambda i, j: graph.add_node((i, j))

        def add_edges(i: int, j: int) -> None:
            for position in self.neighborhood.indexes_for(i, j):
                if (
                    self.get_agent(*position).agent_type == 1
                    and self.get_agent(i, j).agent_type == 1
                ):
                    graph.add_edge((i, j), position)

        self._process_lattice_with(add_nodes)
        self._process_lattice_with(add_edges)

        clusters = [
            length for cluster in nx.connected_components(graph) if (length := len(cluster)) > 1
        ]
        assert len(clusters) > 0, "There is no clusters in the system."
        return sorted(clusters)[-1]
