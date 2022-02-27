from __future__ import annotations

from enum import Enum


class Square:

    class Value(Enum):
        OFF = 0
        ON = 1

    def __init__(self, value: Square.Value):
        self._value = value

    def __eq__(self, other) -> bool:
        return isinstance(other, Square) and other.value == self.value

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return "#" if self.value == Square.Value.ON else "-"

    @property
    def value(self) -> Square.Value:
        return self._value

    def flipped(self) -> Square.Value:
        return Square.Value.ON if self.value == Square.Value.OFF else Square.Value.OFF

