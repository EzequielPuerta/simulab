from itertools import product as cartesian_product
from typing import Any


class ExperimentParameters(dict):  # type: ignore[type-arg]
    def __getattr__(self, parameter_name: str) -> object:
        return self[parameter_name]

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.items() == other.items()


class ExperimentParametersSet:
    def __init__(self, **kwargs):  # type: ignore[no-untyped-def]
        assert all(
            (isinstance(name, str) for name in kwargs.keys())
        ), "Experiment parameter names should be strings."
        assert all(
            (isinstance(values, list) for values in kwargs.values())
        ), "Experiment parameters should be passed using lists."

        self.parameters_to_vary = [name for name, values in kwargs.items() if len(values) > 1]
        names = kwargs.keys()
        self.experiments_parameters = []
        for experiment_parameters in cartesian_product(*kwargs.values()):
            parameters = {name: value for name, value in zip(names, experiment_parameters)}
            self.experiments_parameters.append(ExperimentParameters(**parameters))

        self._raw = dict(**kwargs)
        self.__total = len(self.experiments_parameters)
        self.__index = 0

    def __len__(self) -> int:
        return self.__total

    def __getitem__(self, parameter_name: str) -> Any:
        return self._raw[parameter_name]

    def __iter__(self) -> "ExperimentParametersSet":
        return self

    def __next__(self) -> ExperimentParameters:
        if self.__index < self.__total:
            current = self.experiments_parameters[self.__index]
            self.__index += 1
            return current
        else:
            self.__index = 0
            raise StopIteration
