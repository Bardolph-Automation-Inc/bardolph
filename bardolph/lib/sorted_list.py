import bisect
from typing import Generic, TypeVar

K = TypeVar('K')
T = TypeVar('T')
V = TypeVar('V')


class SortedList(list[T]):
    """
    Sorted list of objects that can keep iterating after one or more of its
    elements disappears, including the current one.

    An instance of this class can be used like a standard Python list. However,
    if the lights are being iterated over slowly enough that the list may be
    updated mid-traversal, it's better to use first() and next().
    """
    @staticmethod
    def _identity(obj):
        return obj

    def __init__(self, key_fn=None):
        self._key_fn = key_fn or self._identity

    def __contains__(self, value: T) -> bool:
        return self._index_of(value) is not None

    def _index_of(self, value: T):
        value = self._key_fn(value)
        pos = bisect.bisect_left(self, value, key=self._key_fn)
        if pos < len(self) and self._key_fn(self[pos]) == value:
            return pos
        return None

    @staticmethod
    def from_list(values):
        new_obj = SortedList()
        for v in values:
            new_obj.add(v)
        return new_obj

    def add(self, value: T) -> None:
        """
        Add a value, but only if it's not already there.
        """
        if self._index_of(value) is None:
            bisect.insort_right(self, value, key=self._key_fn)

    def remove(self, value: T) -> None:
        # It's ok to try to remove a value that's not present.
        pos = self._index_of(value)
        if pos is not None:
            del self[pos]

    def first(self) -> T | None:
        return self[0] if len(self) > 0 else None

    def next(self, value: T) -> T | None:
        if len(self) == 0:
            return None
        pos = bisect.bisect(self, self._key_fn(value), key=self._key_fn)
        return None if pos == len(self) else self[pos]

    def last(self) -> T | None:
        return self[-1] if len(self) > 0 else None

    def prev(self, value: T) -> T | None:
        if len(self) == 0:
            return None
        pos = bisect.bisect_left(self, self._key_fn(value), key=self._key_fn)
        return None if pos == 0 else self[pos - 1]


class _Item(Generic[K, V]):
    def __init__(self, key: K):
        self.key = key
        self.value_list: SortedList[V] = SortedList()


class SortedDict(SortedList[_Item[K, V]]):
    def __init__(self):
        def key_fn(item):
            return item.key
        super().__init__(key_fn)

    def __contains__(self, key: K) -> bool:
        return super().__contains__(_Item(key))

    def add(self, key: K, value: V):
        item = _Item(key)
        pos = self._index_of(item)
        if pos is None:
            item.value_list.add(value)
            super().add(item)
        else:
            self[pos].value_list.add(value)

    def remove(self, key: K, value: V) -> None:
        search_item = _Item(key)
        pos = super()._index_of(search_item)
        if pos is not None:
            item = self[pos]
            value_list = item.value_list
            value_list.remove(value)
            if len(value_list) == 0:
                super().remove(item)

    def remove_all(self, key: K) -> None:
        super().remove(_Item(key))

    def remove_from_all(self, value: V) -> None:
        for key in self.keys():
            self.remove(key, value)

    def first(self) -> tuple[K, V] | None:
        item = super().first()
        if item is None:
            return None, None
        return item.key, item.value_list

    def last(self) -> tuple[K, V] | None:
        item = super().last()
        return None if item is None else item.key, item.value_list

    def next(self, key: K) -> SortedList[V] | None:
        item = super().next(_Item(key))
        return None if item is None else item.value_list

    def prev(self, key: K) -> SortedList[V] | None:
        item = super().prev(_Item(key))
        return None if item is None else item.value_list

    def get(self, key: K) -> SortedList[V] | None:
        pos = self._index_of(_Item(key))
        return None if pos is None else self[pos].value_list

    def has(self, key: K, value: V) -> bool:
        pos = self._index_of(_Item(key))
        return False if pos is None else value in self[pos].value_list

    def keys(self) -> list[K]:
        return [item.key for item in self]

    def values(self) -> list[SortedList[V]]:
        return [item.value_list for item in self]
