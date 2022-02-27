from PathFinding.PathFindingState import PathFindingState, StateTransition
from PathFinding.Algorithms.BasicAlgorithm import BasicAlgorithm

from typing import Optional, Iterable, Tuple, Collection, List, Type, Dict, Generic, TypeVar

TState = TypeVar('TState', bound=PathFindingState)
TTransition = TypeVar('TTransition', bound=StateTransition)


class LookaheadAlgorithm(BasicAlgorithm, Generic[TState]):
    """
    Same basic structure as BasicAlgorithm, but looks ahead some given number of state transitions when
    evaluating the score of any particular state.  This results in many more states to be calculated,
    but it may lead to better results where a transition leads to a temporary increase in score, but is
    still optimal because of better subsequent scores.
    """

    def __init__(self, lookahead_steps: int = 1, **kwargs):
        super(LookaheadAlgorithm, self).__init__(lookahead_steps=lookahead_steps, **kwargs)
        self._lookahead = lookahead_steps
        self._adjacency_cache: Dict[TState, List[Tuple[TState, TTransition]]] = dict()
        self._score_cache: Dict[TState, int] = dict()

    @classmethod
    def name(cls) -> str:
        return "lookahead"

    def get_score(self, state: TState) -> int:

        def _score(current: TState, depth: int) -> int:
            if current in self._score_cache:
                return self._score_cache[current]

            state_value = self._get_state_value(current)

            if current.score == 0:
                return state_value.distance

            if depth <= 0:
                if current not in self._score_cache:
                    self._score_cache[current] = current.score + state_value.distance
                return self._score_cache[current]

            best: Optional[TState] = None
            for s, transition in self._get_adjacent_states(current):
                if s == state_value.previous:
                    continue
                if s not in self._state_map or self._get_state_value(s).distance > state_value.distance + 1:
                    self._add_to_state_map(s, current, transition, state_value.distance + 1)
                if self._has_been_visited(s):
                    continue
                # RECURSIVE STEP FOR ITERATING THROUGH LOOKAHEAD
                if best is None or best.score + state_value.distance > _score(s, depth - 1):
                    best = s

            self._score_cache[current] = best.score + self._get_state_value(best).distance
            return self._score_cache[current]

        try:
            return _score(state, self._lookahead)
        except Exception as e:
            raise e

    def _get_adjacent_states(self, state: TState) -> Iterable[Tuple[TState, TTransition]]:
        if state not in self._adjacency_cache:
            self._adjacency_cache[state] = list(state.get_adjacent_states())
        return self._adjacency_cache[state]
