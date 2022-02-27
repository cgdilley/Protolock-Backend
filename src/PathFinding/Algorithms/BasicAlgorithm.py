from PathFinding.PathFindingState import PathFindingState, StateTransition
from PathFinding.Solution import Solution
from PathFinding.Algorithms.Algorithm import Algorithm
from Errors import ExecutionError, ErrorType
from Interfaces import Comparable, ComparableType
from Utilty import IterableUtils

from abc import ABC, abstractmethod
from typing import Optional, Iterable, Tuple, Collection, List, Type, Dict, Generic, TypeVar, Hashable, Set, Callable

TState = TypeVar('TState', bound=PathFindingState)
TTransition = TypeVar('TTransition', bound=StateTransition)


class StateMapValue(Generic[TState]):

    def __init__(self, state: TState, previous: Optional[TState], move: Optional[StateTransition], distance: int):
        self.state = state
        self.previous = previous
        self.move = move
        self.distance = distance


class BasicAlgorithm(Algorithm[TState, TTransition, Tuple[int, int]], Generic[TState, TTransition]):
    """
    Basically A*
    """

    def __init__(self, **kwargs):
        super(BasicAlgorithm, self).__init__(**kwargs)
        self._visited: Set[TState] = set()
        self._open_list: List[Tuple[TState, Tuple[int, int]]] = []
        self._state_map: Dict[TState, StateMapValue] = dict()

    @classmethod
    def name(cls) -> str:
        return "basic"

    def solve(self, initial_state: TState) -> Solution:
        self._add_to_open_list(initial_state)
        self._add_to_state_map(initial_state, None, None, 0)

        while len(self._open_list) > 0:
            current = self._pop_item_from_open_list()

            if self._check_for_goal(current):
                return self._construct_path(current)

            if self._has_been_visited(current):
                continue

            # print(current.render() + "\n")

            self._add_to_visited(current)
            state_value = self._get_state_value(current)

            # TODO: REMOVE ME
            # if state_value.distance >= 5:
            #     continue

            for state, transition in self._get_adjacent_states(current):
                # print(state.render() + "\n")
                self._add_to_state_map(state, current, transition, state_value.distance + 1)
                if self._has_been_visited(state):
                    continue
                self._add_to_open_list(state)

        raise ExecutionError(ErrorType.NO_PATH_FOUND, "Unable to find path for the given initial state.")

    def _add_to_state_map(self, state: TState, previous: Optional[TState],
                          transition: Optional[TTransition], value: int):
        if state not in self._state_map or self._get_state_value(state).distance > value:
            self._state_map[state] = StateMapValue(state, previous, transition, value)

    def _add_to_open_list(self, state: TState):
        score = self.get_score(state)
        i = IterableUtils.binary_search_by(self._open_list, score,
                                           lambda x: x[1])
        if i < 0:
            i = ~i
        self._open_list.insert(i, (state, score))

    def _add_to_visited(self, state: TState):
        self._visited.add(state)

    def _check_for_goal(self, state: TState) -> bool:
        return state.is_goal()

    def _get_adjacent_states(self, state: TState) -> Iterable[Tuple[TState, TTransition]]:
        yield from state.get_adjacent_states()

    def _pop_item_from_open_list(self) -> TState:
        return self._open_list.pop(0)[0]

    def _get_state_value(self, state: TState) -> StateMapValue:
        try:
            return self._state_map[state]
        except KeyError:
            return StateMapValue(state, None, None, 0)

    def _has_been_visited(self, state: TState) -> bool:
        return state in self._visited

    #

    def _construct_path(self, state: TState) -> Solution:
        path: List[Tuple[TState, TTransition]] = []
        current: TState = state
        while current is not None:
            state_value = self._get_state_value(current)
            path.append((current, state_value.move))
            current = state_value.previous

        return Solution(reversed(path))

    def get_score(self, state: TState) -> Tuple[int, int]:
        try:
            return state.score + self._get_state_value(state).distance
        except KeyError:
            return state.score

