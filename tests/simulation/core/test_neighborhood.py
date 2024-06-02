from src.simulation.core.neighborhood import Moore, VonNeumann


def test_von_neumann_size() -> None:
    assert VonNeumann.size() == 4


def test_moore_size() -> None:
    assert Moore.size() == 8


def test_neighborhood_creation() -> None:
    von_neumann_neighborhood = VonNeumann(30)
    moore_neighborhood = Moore(20)
    assert von_neumann_neighborhood._world_size == 30
    assert moore_neighborhood._world_size == 20


def test_von_neumann_indexes_for() -> None:
    von_neumann_neighborhood = VonNeumann(20)
    position = (5, 2)
    expected_neighbors = [
        (4, 2),
        (5, 1),
        (5, 3),
        (6, 2),
    ]
    neighbors = von_neumann_neighborhood.indexes_for(*position)
    assert len(expected_neighbors) == len(neighbors)
    assert all((each in neighbors for each in expected_neighbors))


def test_moore_indexes_for() -> None:
    moore_neighborhood = Moore(30)
    position = (10, 20)
    expected_neighbors = [
        (9, 19),
        (9, 20),
        (9, 21),
        (10, 19),
        (10, 21),
        (11, 19),
        (11, 20),
        (11, 21),
    ]
    neighbors = moore_neighborhood.indexes_for(*position)
    assert len(expected_neighbors) == len(neighbors)
    assert all((each in neighbors for each in expected_neighbors))


def test_position_normalization() -> None:
    neighborhood = VonNeumann(30)
    assert neighborhood._norm(-1) == 29
    assert neighborhood._norm(0) == 0
    assert neighborhood._norm(1) == 1
    assert neighborhood._norm(29) == 29
    assert neighborhood._norm(30) == 0


def test_von_neumann_border_indexes_for() -> None:
    von_neumann_neighborhood = VonNeumann(20)
    position = (0, 0)
    expected_neighbors = [
        (19, 0),
        (0, 19),
        (0, 1),
        (1, 0),
    ]
    neighbors = von_neumann_neighborhood.indexes_for(*position)
    assert len(expected_neighbors) == len(neighbors)
    assert all((each in neighbors for each in expected_neighbors))


def test_moore_border_indexes_for() -> None:
    moore_neighborhood = Moore(30)
    position = (0, 0)
    expected_neighbors = [
        (29, 29),
        (29, 0),
        (29, 1),
        (0, 29),
        (0, 1),
        (1, 29),
        (1, 0),
        (1, 1),
    ]
    neighbors = moore_neighborhood.indexes_for(*position)
    assert len(expected_neighbors) == len(neighbors)
    assert all((each in neighbors for each in expected_neighbors))
