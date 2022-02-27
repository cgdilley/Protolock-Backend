from __future__ import annotations

from typing import Iterable, Collection, List, Dict, Optional, Callable, TypeVar, Hashable, Any, Generic


T = TypeVar('T')
H = TypeVar('H', bound=Hashable)


def group_by(items: Iterable[T], grouper: Callable[[T], H]) -> Dict[H, List[T]]:
    d: Dict[H, List[T]] = dict()
    for item in items:
        key = grouper(item)
        if key not in d:
            d[key] = [item]
        else:
            d[key].append(item)
    return d


def get_or_default(obj: Dict[H, T], key: H, default: Optional[T] = None) -> Optional[T]:
    if key in obj:
        return obj[key]
    return default
