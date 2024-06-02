# Abstract Model

* [Abstract Grid](#abstract-grid)
* [Abstract Agent](#abstract-agent)
* [Model Evolution](#model-evolution)
* [Series](#series)

---

## Abstract Grid

```python
from src.models.abstract.model import AbstractLatticeModel
```

It includes all the basic behavior of a computable model for a two-dimensional cellular automaton.

Expects classic parameters like:
* `length`: an integer $n$ that defines the final size of the grid $n \times n$.
* `configuration`: an initial grid configuration. If you do not provide one, it will be generated automatically.
* `neighborhood`: the strategy that defines, given a position, which cells will be its neighbors. There are two possible ones implemented:
    * `src.simulation.core.neighborhood.VonNeumann` (default)
    * `src.simulation.core.neighborhood.Moore`
* `agent_types`: the number of agent types available in the grid. Default value: 2.
* `update_simultaneously`: *boolean* value that allows you to indicate to the model if the update of each agent should impact the global configuration, allowing it to impact subsequent updates in the same step (`False`, default value), or if all agents are updated in the same simulation step using a temporal grid and at the end of this process, all temporal changes are impacted in the global grid, thus ensuring that each agent's state is based on the previous grid's state (`True`).

## Abstract Agent

```python
from src.models.abstract.agent import Agent
```

Although initial configurations can be entered into the abstract model (an *array* of $x \in [0..$`agent_types`$)$ of $n \times n$), the grid on which the model works does not ends up being an array of integers, but is one of *agents*, so they can have more complex behavior if necessary.

The abstract model provides a basic abstract agent, which contains a single attribute called `agent_type`. Therefore, if in the entered configuration $M_{T_0}$, we have that $M_{T_0}[i,j] = x$, with $x \in [0..$`agent_types`$)$, in the initial configuration $M_{T_1}$ we will actually have $M_{T_1}[i,j] = $`Agent(agent_type=x)`$.

Then, if the $Y$ model needs more complex behavior from the agents (see the case of the real estate market model), $W$ can be created, which subclasses the `Agent` class and specialize it for the case. When the abstract model is initialized, it uses the `_create_agent` method, so you can reimplement this method in $Y$ to use the new agent model:

```python
from src.models.abstract.agent import Agent
from src.models.abstract.model import AbstractLatticeModel

class W(Agent):
    pass

class Y(AbstractLatticeModel):
    ...
    def _create_agent(self, basic_agent: Agent, i: int, j: int) -> W:
        ...
        return W(agent_type=basic_agent.agent_type)
    ...
```

## Model Evolution

As mentioned, all the basic logic of the automaton is contained in the abstract model. The only method that must define a specific model is the `step`. It must indicate how the model will be updated, agent by agent. Then, depending on the value of `update_simultaneously`, that update will impact either the global configuration or a temporary one.

```python
def step(self, i: int, j: int, **kwargs) -> None:
    pass
```

## Series

The evolution of the model will generate multiple data of interest, iteration by iteration. Different methods can be implemented in the concrete model and decorated with `@as_series`. This will mean that after each global iteration, the result of that method will be stored, generating a series of data to be analyzed at the end of the simulation. The result can be any object, whether integer values, decimals or even snapshots of the grid.

In fact, a series that may be of trivial interest is the grid with its `agent_type` values ​​for each cell, at a given time. The following `agent_types_lattice` method will ensure that we have this information at the end of the simulation:

```python
from src.models.abstract.model import AbstractLatticeModel, as_series

class Y(AbstractLatticeModel):
    ...
    @as_series
    def agent_types_lattice(self) -> List[List[int]]:
        action = lambda i, j: self.get_agent(i, j).agent_type
        return self._process_lattice_with(action)
```

The series will be saved in a `series: dict` attribute, of the simulated model instance. The *key* of the series is the name of the method related to it. That is, if the initial configuration is $M_{T_0}$, for the series in the previous case it is valid:

`Y().series["agent_types_lattice"][0] = ` $M_{T_0}$

There is another similar decorator, called `as_series_with`. It allows two things:

1. Define dependencies for the series. For example, we could have a series that projects a certain attribute for each agent, generating a grid $n \times n$ of that values. And in the other hand, we might need to create a new series that takes the average of the values ​​of the aforementioned grid in each iteration. If we execute the first series method directly, we would be recalculating the entire grid again. In order not to recalculate all the values, we can indicate that the second series depends on the first and then access the values ​​already calculated and stored in the `self.series` attribute.

```python
from src.models.abstract.model import AbstractLatticeModel, as_series

class Y(AbstractLatticeModel):
    ...
    @as_series
    def agent_utilities_lattice(self) -> List[List[int]]:
        action = lambda i, j: self.get_agent(i, j).utility
        return self._process_lattice_with(action)

    @as_series_with(depends=("agent_utilities_lattice",)))
    def total_average_utility_level(self) -> float:
        total_utilities = self._flatten("agent_utilities_lattice")
        return sum(total_utilities) / self.length**2
```
> [!TIP]
> The `_flatten` method is useful for obtaining the latest snapshot of a multidimensional series, for example grids (or lists of lists), in a flattened format (without nested lists).

2. In some cases it may be useful to relate the data obtained in a series with certain *metadata* to be displayed on the *plotters*. This can be achieved using the `as_series_with` decorator mentioned previously.

> [!IMPORTANT]
> This can have a significant computational cost, in space and time. It is not the intention of this code to optimize this procedure, therefore it must be used judiciously.

> [Back](../README.md)
