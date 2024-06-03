from abc import ABC
from functools import total_ordering
from typing import cast


@total_ordering
class Agent(ABC):
    def __init__(
        self,
        agent_type: int,
    ):
        self.agent_type = agent_type

    def __repr__(self) -> str:
        return str(self.agent_type)

    def __add__(self, delta_agent_type: int | object) -> int:
        if isinstance(delta_agent_type, type(self)):
            result = self.agent_type + delta_agent_type.agent_type
        else:
            result = self.agent_type + cast(int, delta_agent_type)
        return result

    def __sub__(self, delta_agent_type: int | object) -> int:
        if isinstance(delta_agent_type, type(self)):
            result = self.agent_type - delta_agent_type.agent_type
        else:
            result = self.agent_type - cast(int, delta_agent_type)
        return result

    def __mul__(self, factor: int | object) -> int:
        if isinstance(factor, type(self)):
            result = self.agent_type * factor.agent_type
        else:
            result = self.agent_type * cast(int, factor)
        return result

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int):
            return self.agent_type == other
        elif isinstance(other, type(self)):
            return self.agent_type == other.agent_type
        else:
            return False

    def __hash__(self) -> int:
        return hash((self.agent_type,))

    def __lt__(self, other: object) -> bool:
        if isinstance(other, int):
            return self.agent_type < other
        elif isinstance(other, type(self)):
            return self.agent_type < other.agent_type
        else:
            return NotImplemented
