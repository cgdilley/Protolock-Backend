from __future__ import annotations

from PathFinding import PathFindingState, StateTransition, Solution, Algorithm, ComparableStateTransition
from Lambda import LambdaArguments
from Errors import ExecutionError, ErrorType
from Interfaces import Comparable, ComparableType

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List, Type, Tuple
import json


TState = TypeVar('TState', bound=PathFindingState)
TTransition = TypeVar('TTransition', bound=StateTransition)
TCompTransition = TypeVar('TCompTransition', bound=ComparableStateTransition)
T = TypeVar('T')


class GameState(PathFindingState, ABC, Generic[TState, TTransition]):

    @classmethod
    @abstractmethod
    def parse(cls, s: str) -> TState: ...

    @abstractmethod
    def render(self) -> str: ...


class GameTransition(StateTransition, ABC, Generic[T]):
    ...


class ComparableGameTransition(ComparableStateTransition, ABC, Generic[ComparableType]):

    @property
    def value(self) -> ComparableType:
        return self._value


TGameState = TypeVar('TGameState', bound=GameState)
TGameTransition = TypeVar('TGameTransition', bound=GameTransition)


class Game(ABC, Generic[TGameState, TGameTransition]):

    def __init__(self, initial_state: TGameState, algorithm: Algorithm):
        self.initial_state = initial_state
        self.algorithm = algorithm

    @classmethod
    @abstractmethod
    def name(cls) -> str: ...

    @classmethod
    @abstractmethod
    def prepare(cls, args: LambdaArguments) -> Game: ...

    @abstractmethod
    def log(self) -> None: ...

    @classmethod
    @abstractmethod
    def supported_algorithms(cls) -> List[Type[Algorithm]]: ...

    def solve(self) -> Solution:
        print(f"Running algorithm '{self.algorithm.name()}' "
              f"(aka. {self.algorithm.__class__.__name__}) with args "
              f"{json.dumps(self.algorithm.kwargs)}...")
        return self.algorithm.solve(self.initial_state)

    def conditions(self) -> Conditions:
        return Conditions(self.algorithm.name(), self.algorithm.kwargs, self.initial_state)

    @classmethod
    def _identify_algorithm(cls, algo_name: str) -> Type[Algorithm]:
        for algo_type in cls.supported_algorithms():
            if algo_type.name() == algo_name:
                return algo_type
        raise ExecutionError(ErrorType.BAD_REQUEST,
                             f"Invalid algorithm '{algo_name}' for "
                             f"game '{cls.name()}'.",
                             {"supported": [a.name() for a in cls.supported_algorithms()]})

    @classmethod
    def _load_algorithm(cls, algo_name: str, algo_args: dict) -> Algorithm:
        algo_type = cls._identify_algorithm(algo_name)
        try:
            return algo_type(**algo_args)
        except Exception as e:
            raise ExecutionError(ErrorType.BAD_REQUEST, "Bad algorithm arguments, could not "
                                                        "prepare algorithm.",
                                 {"given": {"args": algo_args, "error": str(e)}})


class Conditions:

    def __init__(self, algorithm: str, args: dict, state: GameState):
        self.algorithm = algorithm
        self.args = tuple(sorted(args.items(), key=lambda t: t[0]))
        self.state = state

    @property
    def signature(self) -> Tuple:
        return self.algorithm, self.args, self.state

    def __eq__(self, other) -> bool:
        return isinstance(other, Conditions) and self.signature == other.signature

    def __hash__(self) -> int:
        return hash(self.signature)
