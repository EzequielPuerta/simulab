# Computational Models

* [Schelling's Segregation](#schellings-segregation)
* [Real State Market](#real-state-market)
* [Condensation](#condensation)
* [Conway's Game of Life](#conways-game-of-life)

---

## Schelling's Segregation

```python
from simulab.models.computational.schelling.model import Schelling
```

Parameters:
* `tolerance: int`

## Real State Market

```python
from simulab.models.computational.real_state_market.model import RealStateMarket
```

Parameters:
* `alpha: float = 0.5`
* `A: float = 1 / 16`
* `B: float = 0.5`
* `utility_tolerance: float = 0.85`

## Condensation

```python
from simulab.models.computational.condensation.model import Condensation
```

Parameters:
* `probability: float`

## Conway's Game of Life

```python
from simulab.models.computational.game_of_life.model import GameOfLife
from simulab.models.computational.game_of_life.seeds import Seed
```

Parameters:
* `seeds: List[Seed]`

> [Back](../README.md)
