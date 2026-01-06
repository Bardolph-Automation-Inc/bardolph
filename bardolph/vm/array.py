from typing import Self


class ArrayException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


def _out_of_bounds(index):
    raise ArrayException('array index ({}) out of bounds'.format(index))


class ArrayBase:
    def base(self) -> "ArrayCursor":
        pass

    def is_at_leaf(self) -> bool:
        return False


class Array(ArrayBase):
    def __init__(self):
        self._root = None

    def __len__(self):
        return 0 if self._root is None else len(self._root)

    def add_dimension(self, size) -> Self:
        if self._root is None:
            self._root = ArrayBranch(size)
        else:
            self._root.add_branch(size)
        return self

    def base(self) -> "ArrayCursor":
        return ArrayCursor(self._root)


class ArrayBranch(ArrayBase):
    def __init__(self, size):
        self._data = [None] * size
        self._is_leaf = True

    def __len__(self) -> int:
        return len(self._data)

    def is_at_leaf(self) -> bool:
        return self._is_leaf

    def add_branch(self, size) -> None:
        rng = range(0, len(self._data))
        if self._is_leaf:
            for i in rng:
                self._data[i] = ArrayBranch(size)
            self._is_leaf = False
        else:
            for i in rng:
                self._data[i].add_branch(size)

    def base(self) -> "ArrayCursor":
        return ArrayCursor(self)


class ArrayCursor(ArrayBase):
    def __init__(self, branch: ArrayBranch):
        self._branch = branch
        self._offset = None

    def __len__(self) -> int:
        if self._offset is None:
            return len(self._branch)
        return len(self._branch._data[self._offset])

    def base(self) -> Self:
        self._offset = None
        return self

    def index(self, offset) -> Self:
        if self._offset is None:
            self._offset = offset
        else:
            try:
                self._branch = self._branch._data[self._offset]
                self._offset = offset
            except IndexError:
                _out_of_bounds(self._offset)
        return self

    def is_at_leaf(self) -> bool:
        return self._branch.is_at_leaf() and self._offset is not None

    def set_value(self, value) -> None:
        if not self._branch.is_at_leaf():
            raise ArrayException('array not fully dereferenced')
        try:
            self._branch._data[self._offset] = value
        except IndexError:
            _out_of_bounds(self._offset)
        return True

    def get_value(self):
        try:
            return self._branch._data[self._offset]
        except IndexError:
            _out_of_bounds(self._offset)


def _allow_array_set(
        lvalue: ArrayBase, rvalue: ArrayBase | int | float | str) -> bool:
    can_assign = False
    if isinstance(lvalue, Array):
        if (isinstance(rvalue, (Array, ArrayBranch))
                or (isinstance(rvalue, ArrayCursor)
                    and not rvalue.is_at_leaf())):
            can_assign = True
    elif (isinstance(lvalue, ArrayCursor)
            and lvalue.is_at_leaf()
            and not isinstance(rvalue, ArrayBase)):
        can_assign = True
    return can_assign


def array_set(lvalue: ArrayBase, rvalue: ArrayBase | int | float | str) -> None:
    if not _allow_array_set(lvalue, rvalue):
        raise ArrayException('illegal assignment involving an array')

    if isinstance(lvalue, Array):
        if isinstance(rvalue, Array):
            lvalue._root = rvalue._root
        elif isinstance(rvalue, ArrayBranch):
            lvalue._root = rvalue
        elif isinstance(rvalue, ArrayCursor):
            lvalue._root = rvalue._branch._data[rvalue._offset]
    elif isinstance(lvalue, ArrayCursor):
        lvalue.set_value(rvalue)

def assure_rvalue(value):
    return value.get_value() if isinstance(value, ArrayCursor) else value
