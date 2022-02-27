from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Union, Optional, Iterable, Collection


class Formation(ABC):

    @classmethod
    @abstractmethod
    def get_positions(cls, pos: Tuple[int, int]) -> Iterable[Tuple[int, int]]: ...


class CrossFormation(Formation):

    @classmethod
    def get_positions(cls, pos: Tuple[int, int]) -> Iterable[Tuple[int, int]]:
        yield pos
        yield pos[0] - 1, pos[1]
        yield pos[0] + 1, pos[1]
        yield pos[0], pos[1] - 1
        yield pos[0], pos[1] + 1


class PointFormation(Formation):

    @classmethod
    def get_positions(cls, pos: Tuple[int, int]) -> Iterable[Tuple[int, int]]:
        yield pos
