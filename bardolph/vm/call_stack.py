from collections import deque

from .vm_codes import LoopVar

class StackFrame:
    def __init__(self, variables=None, return_addr=None):
        self.vars = variables or {}
        self.return_addr = return_addr or 0

    def clear(self):
        self.vars.clear()
        self.return_addr = 0

class LoopFrame(StackFrame):
    def __init__(self, variables):
        super().__init__(variables, None)
        self._loop_var = {}

    def get_loop_var(self, index):
        return self._loop_var.get(index, None)

    def set_loop_var(self, index, value):
        self._loop_var[index] = value

class CallStack:
    """
    As PARAM instructions are encountered, incoming parameters are saved in
    _current but are out of scope. That StackFrame instance gets pushed when a
    routine is called. The presence of that StackFram at the top of the stack
    brings the parameters into scope.

    Variables are immediately put into the StackFrame referenced by self.top.
    If the stack has only one StackFrame, then declared variables become
    globals. Otherwise, they are local variables that go out of scope when the
    routine returns.
    """

    def __init__(self):
        """
        Put an empty StackFrame into the stack as the root context. Create
        a new StackFrame to accumulate parameters during set-up for a routine
        invocation.
        """
        self._stack = deque()
        self._root_frame = StackFrame()
        self._stack.append(self._root_frame)
        self._current = StackFrame()
        self._constants = {}

    def reset(self) -> None:
        self._stack.clear()
        self._root_frame.clear()
        self._stack.append(self._root_frame)
        self._current.clear()
        self._constants.clear()

    @property
    def top(self) -> StackFrame:
        return self._stack[-1]

    def put_param(self, name, value) -> None:
        self._current.vars[name] = value

    def put_constant(self, name, value) -> None:
        if name not in self._constants:
            self._constants[name] = value

    def put_variable(self, index, value) -> None:
        if isinstance(index, LoopVar):
            assert isinstance(self.top, LoopFrame)
            return self.top.set_loop_var(index, value)
        dest = self._root_frame if index in self._root_frame.vars else self.top
        dest.vars[index] = value

    def is_param(self, name) -> bool:
        return name in self.top.vars

    def set_return(self, address) -> None:
        self._current.return_addr = address

    def get_return(self) -> int:
        return self.top.return_addr

    def get_variable(self, name):
        if isinstance(name, LoopVar):
            if isinstance(self.top, LoopFrame):
                return self.top.get_loop_var(name)
            return None
        for place in (self._constants, self.top.vars, self._root_frame.vars):
            if name in place:
                return place[name]
        return None

    def push_current(self) -> None:
        self._stack.append(self._current)
        self._current = StackFrame()

    def enter_loop(self) -> None:
        self._stack.append(LoopFrame(self.top.vars))

    def exit_loop(self) -> None:
        assert len(self._stack) > 1
        self._stack.pop()

    def unwind_loops(self) -> None:
        while isinstance(self.top, LoopFrame):
            self._stack.pop()

    def pop_current(self) -> None:
        assert len(self._stack) > 1
        self._current = self._stack.pop()
        self._current.clear()
