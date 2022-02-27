from PathFinding import PathFindingState, StateTransition
from Interfaces import JSONable

from typing import TypeVar, Generic, Iterable, Tuple, List, Dict, Optional, Iterator

TState = TypeVar('TState', bound=PathFindingState)
TTransition = TypeVar('TTransition', bound=StateTransition)


class Solution(JSONable, Generic[TState, TTransition]):

    def __init__(self, steps: Iterable[Tuple[TState, Optional[TTransition]]]):
        self.steps = list(steps)

    def __len__(self) -> int:
        return len(self.steps)

    def __iter__(self) -> Iterator[Tuple[TState, TTransition]]:
        return iter(self.steps)

    def to_json(self) -> dict:
        return {"steps": [{"state": state.to_json(),
                           **({"transition": transition.to_json()} if transition is not None else {})}
                          for state, transition in self.steps]}
