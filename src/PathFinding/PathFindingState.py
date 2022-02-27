from __future__ import annotations

from Interfaces import Comparable, ComparableType, JSONable, CompareAndHashableType, CompareAndHashable

from abc import ABC, abstractmethod
from typing import Generic, Iterable, TypeVar, Tuple, Hashable

THashable = TypeVar('THashable', bound=Hashable)


class StateTransition(JSONable, ABC, Generic[THashable]):

    def __init__(self, value: THashable):
        self._value = value

    @property
    def value(self) -> THashable:
        return self._value

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other) -> bool:
        return isinstance(other, StateTransition) and self.value == other.value

    def __hash__(self) -> int:
        return hash(self.value)


TTransition = TypeVar('TTransition', bound=StateTransition)


class PathFindingState(JSONable, ABC, Generic[CompareAndHashableType, TTransition]):

    @property
    @abstractmethod
    def score(self) -> CompareAndHashableType: ...

    @abstractmethod
    def get_adjacent_states(self) -> Iterable[Tuple[PathFindingState, TTransition]]: ...

    @abstractmethod
    def is_goal(self) -> bool: ...

    @abstractmethod
    def transition(self, transition: TTransition) -> PathFindingState: ...


class ComparableStateTransition(StateTransition[CompareAndHashable], ABC, Generic[CompareAndHashableType]):

    def __lt__(self, other) -> bool:
        return self.value < other.value
