from collections import deque

class StackFrame:
    def __init__(self):
        self.vars = {}
        self.return_addr = 0

    def clear(self):
        self.vars.clear()
        self.return_addr = 0


class CallStack:
    """
    Incoming parameters are saved in _current but are out of scope. That
    StackFrame gets pushed when a routine is called, which brings the
    parameters into scopt.

    Variables are immediately put into the StackFrame referenced by self.top.
    If the stack has only one StackFrame, then declared variables become
    globals. Otherwise, they are local variables that go out of scopt when the
    routine returns.
    """

    def __init__(self):
        """
        Put an empty StackFrame into the stack as the root context. Create
        a new StackFrame to accumulate parameters during set-up for a routine
        invocation.
        """
        self._externs = {}
        self._stack = deque()
        self._root_frame = StackFrame()
        self._stack.append(self._root_frame)
        self._current = StackFrame()

    @property
    def top(self) -> StackFrame:
        return self._stack[-1]

    def put_param(self, name, value) -> None:
        self._current.vars[name] = value

    def put_variable(self, name, value) -> None:
        self.top.vars[name] = value

    def is_param(self, name) -> bool:
        return name in self.top.vars

    def set_return(self, address) -> None:
        self._current.return_addr = address

    def get_return(self) -> int:
        return self.top.return_addr

    def clear(self) -> None:
        self._externs.clear()
        self._stack.clear()
        self._current.clear()
        self._root_frame = StackFrame()
        self._stack.append(self._root_frame)

    def get_variable(self, name):
        # Return the value of the named parameter or a bound variable. In the
        # case of a name conflict, the parameter in the script wins.
        #
        # If the stack has more than one StackFrame, and if the top of the
        # stack doesn't have the requested variable, also check the StackFrame
        # referenced by self._root_frame, which contains the globals.
        #
        value = None
        frame = self.top
        if name in frame.vars:
            value = frame.vars[name]
        elif len(self._stack) > 1 and name in self._root_frame.vars:
            value = self._root_frame.vars[name]
        elif name in self._externs:
            value = self._externs[name].value
        return value

    def bind(self, name, extern):
        self._externs[name] = extern

    def unbind(self, name):
        if name in self._externs:
            del self._externs[name]

    def unbind_all(self):
        self._externs.clear()

    def push_current(self) -> None:
        self._stack.append(self._current)
        self._current = StackFrame()

    def pop_current(self) -> None:
        assert len(self._stack) > 1
        self._current = self._stack.pop()
        self._current.clear()
