from __future__ import annotations

from PathFinding.Solution import Solution
from PathFinding.PathFindingState import PathFindingState, StateTransition, ComparableStateTransition
from PathFinding.Algorithms.BasicAlgorithm import BasicAlgorithm, StateMapValue
from PathFinding.Algorithms.LookaheadAlgorithm import LookaheadAlgorithm

from typing import Optional, Iterable, Tuple, Collection, List, Type, Dict, Generic, TypeVar, Set

TState = TypeVar('TState', bound=PathFindingState)
TTransition = TypeVar('TTransition', bound=StateTransition)
TCompTransition = TypeVar('TCompTransition', bound=ComparableStateTransition)


class OrderlessStateMapValue(StateMapValue, Generic[TCompTransition]):

    def __init__(self, state: TState, previous: Optional[TState], moves: Tuple[TCompTransition, ...]):
        super(OrderlessStateMapValue, self).__init__(
            state, previous, moves[-1] if len(moves) > 0 else None, len(moves))
        self.ordered_moves = moves
        self.moves = tuple(sorted(moves))

    def append(self, state: TState, move: TCompTransition) -> OrderlessStateMapValue:
        if move in self.ordered_moves:
            return OrderlessStateMapValue(state, self.state, tuple(m for m in self.ordered_moves if m != move))
        return OrderlessStateMapValue(state, self.state, self.ordered_moves + (move,))


class OrderlessAlgorithm(BasicAlgorithm[TState, TCompTransition], Generic[TState, TCompTransition]):
    """
    This algorithm treats all combinations of transitions as identical, regardless of the order they are in.
    It also treats two instances of the same transition as cancelling each other out, which may be a bad generalization,
    but fits for this purpose.

    To accomplish this, this algorithm only replaces how interactions occur with the list of visited states and the
    mapping of states to their optimal route from the starting state.  Otherwise, everything else is leveraged
    as-is from BasicAlgorithm.
    """

    def __init__(self, **kwargs):
        super(OrderlessAlgorithm, self).__init__(**kwargs)
        self._visited_combinations: Dict[Tuple[TCompTransition, ...], TState] = dict()

    @classmethod
    def name(cls) -> str:
        return "orderless"

    def _has_been_visited(self, state: TState) -> bool:
        return super()._has_been_visited(state) or \
               self._get_path_combination(state) in self._visited_combinations
        # return self._get_path_combination(state) in self._visited_combinations

    def _add_to_visited(self, state: TState):
        super()._add_to_visited(state)
        self._visited_combinations[self._get_path_combination(state)] = state

    def _get_path_combination(self, state: TState) -> Tuple[TCompTransition]:
        return self._get_state_value(state).moves

    def _add_to_state_map(self, state: TState, previous: Optional[TState],
                          transition: Optional[TCompTransition], value: int):
        # if state in self._state_map:
        #     return
        if transition is None:
            self._state_map[state] = OrderlessStateMapValue(state, None, tuple())
        else:
            state_value = self._get_state_value(previous)
            if state not in self._state_map or state_value.distance > value:
                self._state_map[state] = state_value.append(state, transition)

    def _get_state_value(self, state: TState) -> OrderlessStateMapValue[TCompTransition]:
        try:
            return self._state_map[state]
        except KeyError:
            return OrderlessStateMapValue(state, None, tuple())

    def _construct_path(self, state: TState) -> Solution:
        def _path() -> Iterable[Tuple[TState, Optional[TCompTransition]]]:
            steps = self._get_state_value(state).moves
            current = state
            for step in reversed(steps):
                yield current, step
                current = current.transition(step)
            yield current, None

        return Solution(reversed(list(_path())))


#


class OrderlessLookaheadAlgorithm(OrderlessAlgorithm, LookaheadAlgorithm):

    @classmethod
    def name(cls) -> str:
        return "orderless_lookahead"
