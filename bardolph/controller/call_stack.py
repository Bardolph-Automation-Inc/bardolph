from collections import deque

class StackFrame:
    def __init__(self):
        self.params = {}
        self.return_addr = 0

    def clear(self):
        self.params.clear()
        self.return_addr = 0


class CallStack:
    def __init__(self):
        self._stack = deque()
        self._current = StackFrame()

    @property
    def top(self) -> StackFrame:
        return self._stack[-1] if len(self._stack) > 0 else None

    def add_param(self, name, value) -> None:
        self._current.params[name] = value

    def is_param(self, name) -> bool:
        return self.top is not None and name in self.top.params

    def set_return(self, address) -> None:
        self._current.return_addr = address

    def get_return(self) -> int:
        return None if self.top is None else self.top.return_addr

    def clear(self) -> None:
        self._stack.clear()
        self._current.clear()

    def get_variable(self, name):
        # Returns the value of the named parameter.
        return None if self.top is None else self.top.params.get(name, None)

    def push_current(self) -> None:
        self._stack.append(self._current)
        self._current = StackFrame()

    def pop_current(self) -> None:
        self._current = self._stack.pop()
        self._current.clear()
