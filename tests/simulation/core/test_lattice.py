from src.simulation.core.lattice import Lattice


def test_lattice_shape() -> None:
    grid_1 = Lattice.zeros(3)
    grid_2 = Lattice.zeros(5)
    assert grid_1.length == 3
    assert grid_2.length == 5


def test_custom_lattice() -> None:
    configuration = [[10, 10, 10], [10, 10, 10], [10, 10, 10]]
    grid = Lattice(configuration)
    assert grid.configuration == configuration
    assert grid.length == 3


def test_update_with() -> None:
    configuration = [[10, 10, 10], [10, 10, 10], [10, 10, 10]]
    grid = Lattice(configuration)
    for row in grid.configuration:
        for cell in row:
            assert cell == 10

    configuration = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
    grid = Lattice(configuration)
    for row in grid.configuration:
        for cell in row:
            assert cell == 1


def test_lattice_full_of_tens() -> None:
    grid = Lattice.full(10, 3)
    assert grid.configuration == [[10, 10, 10], [10, 10, 10], [10, 10, 10]]


def test_lattice_full_of_zeros() -> None:
    grid = Lattice.zeros(3)
    assert grid.configuration == [[0, 0, 0], [0, 0, 0], [0, 0, 0]]


def test_lattice_full_of_ones() -> None:
    grid = Lattice.ones(3)
    assert grid.configuration == [[1, 1, 1], [1, 1, 1], [1, 1, 1]]


def test_lattice_random() -> None:
    grid = Lattice.random(2, 3)
    for row in grid.configuration:
        for cell in row:
            assert cell in range(2)


def test_lattice_at() -> None:
    grid = Lattice.zeros(3)
    assert all([grid.at(i, j) == 0 for i in range(3) for j in range(3)])
