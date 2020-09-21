import bisect

class SortedList(list):
    """
    Sorted list of objects that can keep iterating after one or more of its
    elements disappears, including the current one.
    """
    def __init__(self, initial=None):
        if initial is not None:
            if isinstance(initial, str):
                self.append(initial)
            else:
                self.extend(sorted(initial))

    def _index_of(self, value):
        pos = bisect.bisect_left(self, value)
        if pos != len(self) and self[pos] == value:
            return pos
        return None

    def add(self, value) -> None:
        if self._index_of(value) is None:
            bisect.insort(self, value)

    def remove(self, value) -> None:
        pos = self._index_of(value)
        if pos is not None:
            del self[pos]

    def first(self):
        return self[0] if len(self) > 0 else None

    def next(self, value):
        if len(self) == 0:
            return None
        pos = bisect.bisect(self, value)
        return None if pos == len(self) else self[pos]

    def last(self):
        return self[-1] if len(self) > 0 else None

    def prev(self, value):
        if len(self) == 0:
            return None
        pos = bisect.bisect_left(self, value)
        return None if pos == 0 else self[pos - 1]

    def has(self, value) -> bool:
        return self._index_of(value) is not None
