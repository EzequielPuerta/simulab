from typing import List, cast

from simulab.models.abstract.model import AbstractLatticeModel, as_series
from simulab.models.computational.game_of_life.seeds import Seed
from simulab.simulation.core.lattice import Lattice


class GameOfLife(AbstractLatticeModel):
    ALIVE = 1
    DEAD = 0

    def __init__(self, seeds: List[Seed], *args, **kwargs):  # type: ignore[no-untyped-def]
        length = kwargs.get("length")
        configuration = kwargs.get("configuration", Lattice.zeros(cast(int, length)))
        self.seeds = seeds
        for seed in self.seeds:
            seed.apply_on(configuration)

        super(GameOfLife, self).__init__(
            *args,
            configuration=configuration,  # type: ignore[misc]
            update_simultaneously=True,
            **kwargs,
        )

    def step(
        self,
        i: int,
        j: int,
        configuration: Lattice,
    ) -> None:
        amount = self.similar_neighbors_amount(i, j, agent_type=self.ALIVE)
        if self.get_agent(i, j).agent_type == self.ALIVE:
            if amount in [2, 3]:
                new_state = self.ALIVE
            else:
                new_state = self.DEAD
        else:
            if amount == 3:
                new_state = self.ALIVE
            else:
                new_state = self.DEAD
        configuration.at(i, j).agent_type = new_state

    @as_series
    def agent_types_lattice(self) -> List[List[int]]:
        action = lambda i, j: self.get_agent(i, j).agent_type
        return self._process_lattice_with(action)
