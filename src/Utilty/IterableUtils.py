from typing import List, Callable, TypeVar
from Interfaces import ComparableType

T = TypeVar('T')


def binary_search_by(items: List[T], val: ComparableType, key=Callable[[T], ComparableType]) -> int:
    """
    Performs a binary search for the given value on the items in the given sorted list with the given key
    function applied.  If a match is found, then the lowest index where a match is found is returned.
    Otherwise, the bit-wise inverse (~) of the index where the value belongs is returned.  If the given
    list is not sorted, this function will return nonsensical results.

    This means that if the returned value is < 0, the value is not found, and if >= 0, it is found.

    If you want to insert a value at the correct index when the returned value 'x' is < 0, then insert
    at '~x'.

    :param items: The sorted items to search.
    :param val: The key value to search for
    :param key: The function to apply to elements of the given list, which converts the type of the elements
    into the type of the val being searched for.
    :return: If a match is found, returns the index of the lowest-index match.  If a match is not found,
    returns the bit-wise inverse of the index where the value could be inserted to maintain sorted order.
    """
    left = 0
    right = len(items)
    while True:
        mid = int((left + right) / 2)
        if not (0 <= mid < len(items)):
            return ~mid
        mid_val = key(items[mid])
        # if mid_val == val:
        #     for i in range(mid-1, -1, -1):
        #         span_val = key(items[i])
        #         if span_val != val:
        #             return i + 1
        #     return 0
        if mid_val < val:
            left = mid + 1
        else:
            right = mid
        if left >= right:
            # return ~left
            return left if 0 <= left < len(items) and key(items[left]) == val else ~left


def binary_search(items: List[ComparableType], val: ComparableType) -> int:
    """
    Performs a binary search for the given value on the items in the given sorted list.
    If a match is found, then the lowest index where a match is found is returned.
    Otherwise, the bit-wise inverse (~) of the index where the value belongs is returned.  If the given
    list is not sorted, this function will return nonsensical results.

    This means that if the returned value is < 0, the value is not found, and if >= 0, it is found.

    If you want to insert a value at the correct index when the returned value 'x' is < 0, then insert
    at '~x'.

    :param items: The sorted items to search
    :param val: The value to search for
    :return: If a match is found, returns the index of the lowest-index match.  If a match is not found,
    returns the bit-wise inverse of the index where the value could be inserted to maintain sorted order.
    """
    return binary_search_by(items, val, lambda x: x)
