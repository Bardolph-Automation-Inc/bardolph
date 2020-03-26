from collections import deque

class EvalStack:
    def __init__(self):
        self._stack = deque()

    def clear(self):
        self._stack.clear()

    @property
    def top(self):
        return self.below(0)

    def below(self, depth):
        return self._stack[-(depth + 1)]

    def push(self, value):
        self._stack.append(value)

    def pop(self):
        assert len(self._stack) > 0
        return self._stack.pop()

    def replace_top(self, value):
        self._stack[-1] = value
