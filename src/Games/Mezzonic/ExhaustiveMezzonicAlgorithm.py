from Interfaces import ComparableType
from PathFinding import Algorithm, PathFindingState, StateTransition, Solution
from Games.Mezzonic.Board import BoardTransition, Board
from Games.Mezzonic.Formation import CrossFormation
from Games.Mezzonic.Square import Square
from Errors import ExecutionError, ErrorType
from Utilty import IterableUtils

from typing import Set, Tuple, Iterable, List, Dict, Optional, Collection, Type
from abc import ABC, abstractmethod


class ExhaustiveMezzonicAlgorithm(Algorithm):
    """
    This algorithm attempts to do an exhaustive (but intelligent) search through all combinations of transitions
    to eventually find the end state.
    There are several modes in which this operates:

    - breadth_first:  Operates basically like a breadth-first tree traversal.  All 1-step solutions are attempted,
    then all 2-step solutions, etc, until the solution is found.
    - sorted_breadth_first:  Operates similarly to breadth_first, but new paths found are added to the queue
    in sorted order, meaning that a promising 2-step solution may be inspected before all 1-step solutions have been.
    - depth_first:  Operates basically like a depth-first tree traversal.  This method is kinda dumb for this purpose,
    and can probably just be ignored.
    - mixed:  This operates as a sort of mix between breadth- and depth-first searching, leveraging the ability to
    sort transitions by potential value.  To start with, all initial moves are considered and ranked, but from there,
    it only inspects the highest-ranked transitions from those states in a depth-first fashion, ignoring any other
    transitions.  If no solution is found, it moves back to level 1 of this tree and does the same thing again.
    Since the algorithm prevents inspecting the same collection of transitions more than once (and thus excludes them
    from being ranked more than once), eventually this will explore all combinations.
    """

    def __init__(self, limit: int = 0, mode: str = "breadth_first", **kwargs):
        super(ExhaustiveMezzonicAlgorithm, self).__init__(limit=limit, mode=mode, **kwargs)
        self.limit = limit
        if mode not in MODES:
            raise ExecutionError(ErrorType.BAD_REQUEST, f"Invalid mode '{mode}'.",
                                 {"given": {"mode": mode}, "allowed": list(MODES.keys())})
        self.mode = MODES[mode](self.limit)

    @classmethod
    def name(cls) -> str:
        return "exhaustive"

    def solve(self, initial_state: Board) -> Solution:

        solution = self.mode.solve(initial_state)

        if solution is None:
            if self.limit > 0:
                raise ExecutionError(ErrorType.NO_PATH_FOUND, f"Unable to find path of length <= {self.limit}.")
            raise ExecutionError(ErrorType.NO_PATH_FOUND, f"No path exists.")

        def _follow_path() -> Iterable[Tuple[Board, Optional[BoardTransition]]]:
            current = initial_state
            yield current, None
            for move in solution:
                current = current.flip_formation(move, formation=CrossFormation)
                yield current, BoardTransition(move)

        return Solution(_follow_path())


#


#


class _SearchMode(ABC):

    def __init__(self, limit: int):
        self.limit = limit

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        ...

    @abstractmethod
    def solve(self, board: Board) -> Optional[Collection[Tuple[int, int]]]:
        ...

    def _generate_open_list(self, board: Board, history: Collection[Tuple[int, int]]):
        open_list: List[Tuple[Tuple[int, int], int]] = []
        for row, col in board.coordinates():
            if (row, col) in history:
                continue
            adjacent_squares = [s for s in (board.get_square(r, c)
                                            for r, c in CrossFormation.get_positions((row, col)))
                                if s is not None]
            adjacent_count = sum(1 for s in adjacent_squares if s.value == Square.Value.ON)
            if adjacent_count == 0:
                continue
            score = board.score + len(adjacent_squares) - (2 * adjacent_count)
            i = IterableUtils.binary_search_by(open_list, score, key=lambda o: o[1])
            if i < 0:
                i = ~i
            open_list.insert(i, ((row, col), score))
        return open_list


class _BreadthFirstMode(_SearchMode):

    @classmethod
    def name(cls) -> str:
        return "breadth_first"

    def solve(self, board: Board) -> Optional[Collection[Tuple[int, int]]]:
        queue: List[Tuple[Board, Tuple[Tuple[int, int], ...], int]] = [(board, tuple(), 0)]
        visited: Set[Tuple[Tuple[int, int], ...]] = set()

        while len(queue) > 0:
            current, history, score = queue.pop(0)

            if len(history) > self.limit:
                continue

            open_list = self._generate_open_list(current, history)

            for move, score in open_list:
                new_history = tuple(sorted(history + (move,)))
                if score == 0:
                    return new_history

                if new_history in visited:
                    continue

                self._add_to_queue(queue, board.flip_formation(move, formation=CrossFormation), new_history, score)

    def _add_to_queue(self, queue: List[Tuple[Board, Tuple[Tuple[int, int], ...], int]],
                      board: Board, history: Tuple[Tuple[int, int], ...], score: int):
        queue.append((board, history, score))


class _SortedBreadthFirstMode(_BreadthFirstMode):

    @classmethod
    def name(cls) -> str:
        return "sorted_breadth_first"

    def _add_to_queue(self, queue: List[Tuple[Board, Tuple[Tuple[int, int], ...], int]], board: Board,
                      history: Tuple[Tuple[int, int], ...], score: int):
        total_score = score + len(history)
        i = IterableUtils.binary_search_by(queue, total_score, key=lambda q: q[2])
        if i < 0:
            i = ~i
        queue.insert(i, (board, history, total_score))


class _MixedMode(_SearchMode):

    def __init__(self, limit: int):
        super(_MixedMode, self).__init__(limit)
        self._visited: Dict[Tuple[Tuple[int, int], ...], Board] = dict()

    @classmethod
    def name(cls) -> str:
        return "mixed"

    def solve(self, board: Board) -> Optional[Collection[Tuple[int, int]]]:
        return self._solve(board, set(), board.width * board.height)

    def _initiate_solve_recursion(self, board: Board, history: Set[Tuple[int, int]]) \
            -> Optional[Collection[Tuple[int, int]]]:
        return self._solve(board, history, 1)

    def _solve(self, board: Board, history: Set[Tuple[int, int]], narrowness: int) \
            -> Optional[Collection[Tuple[int, int]]]:
        if len(history) >= self.limit > 0:
            return None

        open_list = self._generate_open_list(board, history)

        for i, (move, score) in enumerate(open_list):
            if i > narrowness:
                continue
            new_history = history.union({move})
            if score == 0:
                return new_history

            sorted_history = tuple(sorted(new_history))
            if sorted_history in self._visited:
                continue

            new_board = board.flip_formation(move, formation=CrossFormation)
            self._visited[sorted_history] = new_board

            solution = self._initiate_solve_recursion(new_board, new_history)

            if solution is not None:
                return solution

        return None


class _DepthFirstMode(_MixedMode):

    @classmethod
    def name(cls) -> str:
        return "depth_first"

    def _initiate_solve_recursion(self, board: Board, history: Set[Tuple[int, int]]) \
            -> Optional[Collection[Tuple[int, int]]]:
        return self._solve(board, history, board.width * board.height)


#


MODES: Dict[str, Type[_SearchMode]] = {
    m.name(): m for m in [_BreadthFirstMode, _SortedBreadthFirstMode, _MixedMode, _DepthFirstMode]
}
