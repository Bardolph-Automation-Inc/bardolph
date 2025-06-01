class ArrayError: pass

class Array:
    def __init__(self, size):
        self._pos = 0
        self._root = _ArrayBranch(size)
        self._child_ptr = self._root

    def add_dimension(self, size):
        self._child_ptr = self._child_ptr.add_dimension(size)

    def deref(self, index=None):
        self._child_ptr = self._root
        self._pos = index
        return self

    def index(self, sub_index):
        if self._pos is not None:
            self._child_ptr = self._child_ptr.get_value(self._pos)
        self._pos = sub_index
        return self

    def get_value(self):
        if self._pos is not None:
            return self._child_ptr.get_value(self._pos)
        return self

    def set_value(self, value):
        return self._child_ptr.set_value(self._pos, value)


class _ArrayBranch:
    def __init__(self, size):
        self._data = [None] * size
        self._pos = None
        self._leaf = True

    @property
    def is_leaf(self) -> bool:
        return self._leaf

    def add_dimension(self, size):
        for i in range(0, len(self._data)):
            self._data[i] = _ArrayBranch(size)
        self._leaf = False
        return self

    def deref(self, index):
        return self._data[index]

    def get_value(self, index):
        return self._data[index]

    def set_value(self, index, value):
        self._data[index] = value
