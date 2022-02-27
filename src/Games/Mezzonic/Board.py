from __future__ import annotations

from Games.Mezzonic.Square import Square
from Games.Mezzonic.Formation import Formation, PointFormation, CrossFormation
from Games.Game import GameState, GameTransition, ComparableGameTransition

from typing import List, Collection, Union, Tuple, Dict, Iterable, Type, Optional


class Board(GameState):

    def __init__(self, size: Tuple[int, int], values: Dict[Tuple[int, int], Square.Value]):
        self._height, self._width = size
        self._board: Tuple[Tuple[Square]] = \
            tuple(tuple(Square(values[(row, col)] if (row, col) in values else Square.Value.OFF)
                        for col in range(self._width)) for row in range(self._height))
        self._hash_cache: Optional[int] = None

    def __eq__(self, other: Board) -> bool:
        return isinstance(other, Board) and \
               all(all(self._board[row][col] == other._board[row][col]
                       for col in range(self.width))
                   for row in range(self.height))

    def __hash__(self) -> int:
        if self._hash_cache is None:
            self._hash_cache = hash(self._board)
        return self._hash_cache

    def __str__(self) -> str:
        return "|".join("".join("0" if s.value == Square.Value.OFF else "1"
                                for s in row)
                        for row in self._board)

    def __repr__(self) -> str:
        return str(self)

    @property
    def score(self) -> int:
        return sum(1 for row, col in self.coordinates() if self._board[row][col].value == Square.Value.ON)

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    def get_square(self, row: int, col: int) -> Optional[Square]:
        return self._board[row][col] if 0 <= row < self.height and 0 <= col < self.width else None

    def coordinates(self) -> Iterable[Tuple[int, int]]:
        yield from ((row, col) for col in range(self.width) for row in range(self.height))

    def interesting_coordinates(self) -> Iterable[Tuple[int, int]]:
        yield from ((row, col) for row, col in self.coordinates()
                    if any(self._board[r][c].value == Square.Value.ON
                           for r, c in CrossFormation.get_positions((row, col))
                           if 0 <= r < self.height and 0 <= c < self.width))
        # yield from self.coordinates()

    def render(self) -> str:
        return "\n".join(
            " ".join(str(self._board[row][col]) for col in range(self.width)) for row in range(self.height))

    def _to_value_map(self) -> Dict[Tuple[int, int], Square.Value]:
        return {(row, col): self._board[row][col].value for row, col in self.coordinates()}

    def set_values(self, pos: Tuple[int, int], value: Square.Value) -> Board:
        row, col = pos
        value_map = self._to_value_map()
        if 0 <= row < self.height and 0 <= col < self.width:
            value_map[(row, col)] = value
        return Board((self.height, self.width), value_map)

    def flip_values(self, *pos: Tuple[int, int]) -> Board:
        value_map = self._to_value_map()
        for p in pos:
            row, col = p
            if 0 <= row < self.height and 0 <= col < self.width:
                value_map[(row, col)] = self._board[row][col].flipped()
        return Board((self.height, self.width), value_map)

    def flip_formation(self, pos: Tuple[int, int], formation: Type[Formation]) -> Board:
        return self.flip_values(*formation.get_positions(pos))

    def get_adjacent_states(self) -> Iterable[Tuple[Board, BoardTransition]]:
        yield from ((self.transition(transition), transition)
                    for transition in (BoardTransition(pos) for pos in self.coordinates()))

    def is_goal(self) -> bool:
        return self.score == 0

    def transition(self, transition: BoardTransition) -> Board:
        return self.flip_formation(transition.value, CrossFormation)

    @classmethod
    def parse(cls, s: str) -> Board:
        rows = s.split("|")
        if len(rows) == 0 or any(len(r) != len(rows[0]) for r in rows[1:]):
            raise Exception("Invalid board definition, could not parse.")
        return Board((len(rows), len(rows[0])), {
            (r, c): Square.Value(int(rows[r][c]))
            for r in range(len(rows)) for c in range(len(rows[0]))
        })

    def to_json(self) -> dict:
        return {
            "size": {"width": self.width, "height": self.height},
            "squares": [[self._board[r][c].value.value
                         for c in range(self.width)]
                        for r in range(self.height)]
        }


class BoardTransition(ComparableGameTransition[Tuple[int, int]]):

    @property
    def value(self) -> Tuple[int, int]:
        return self._value

    def to_json(self) -> dict:
        return {"row": self.value[0], "col": self.value[1]}
