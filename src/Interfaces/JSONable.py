from __future__ import annotations


from abc import ABC, abstractmethod


class JSONable(ABC):

    @abstractmethod
    def to_json(self) -> dict: ...


class JSONExchangeable(JSONable, ABC):

    @staticmethod
    @abstractmethod
    def from_json(o: dict): ...
