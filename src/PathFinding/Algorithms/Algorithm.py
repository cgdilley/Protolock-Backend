from PathFinding.PathFindingState import PathFindingState, StateTransition
from PathFinding.Solution import Solution
from Errors import ExecutionError, ErrorType
from Interfaces import Comparable, ComparableType
from Utilty import IterableUtils

from abc import ABC, abstractmethod
from typing import Optional, Iterable, Tuple, Collection, List, Type, Dict, Generic, TypeVar, Hashable, Set, Callable

TState = TypeVar('TState', bound=PathFindingState)
TTransition = TypeVar('TTransition', bound=StateTransition)


class Algorithm(ABC, Generic[TState, TTransition, ComparableType]):

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @classmethod
    @abstractmethod
    def name(cls) -> str: ...

    @abstractmethod
    def solve(self, initial_state: TState) -> Solution: ...

    def get_score(self, state: TState) -> Comparable:
        return state.score
