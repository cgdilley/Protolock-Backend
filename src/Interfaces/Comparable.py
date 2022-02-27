from __future__ import annotations


from abc import abstractmethod
from typing import TypeVar, Hashable
from typing_extensions import Protocol


class Comparable(Protocol):

    @abstractmethod
    def __lt__(self: ComparableType, other: ComparableType) -> bool: ...


ComparableType = TypeVar("ComparableType", bound=Comparable)


class CompareAndHashable(Hashable, Protocol):

    @abstractmethod
    def __lt__(self: CompareAndHashableType, other: CompareAndHashableType) -> bool: ...


CompareAndHashableType = TypeVar('CompareAndHashableType', bound=CompareAndHashable)
