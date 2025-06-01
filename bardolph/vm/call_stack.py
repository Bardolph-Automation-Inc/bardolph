from bardolph.vm.array import Array
from bardolph.vm.vm_codes import LoopVar


class StackFrame:
    def __init__(self, parent=None):
        self.parent = parent
        self.vars = parent.vars if parent is not None else {}
        self.constants = parent.constants if parent is not None else None
        self.globals = parent.globals if parent is not None else self.vars
        self.params = {}
        self.return_addr = None

    def put_variable(self, index, value) -> None:
        if index in self.params:
            dest = self.params
        elif index in self.globals:
            dest = self.globals
        else:
            dest = self.vars
        dest[index] = value

    def put_constant(self, name: str, value) -> None:
        self.constants[name] = value

    def get_variable(self, identifier):
        for place in (self.constants, self.vars, self.params, self.globals):
            if identifier in place:
                return place[identifier]
        return None

    def get_parameter(self, name):
        return self.params.get(name, None)


class LoopFrame(StackFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._loop_var = {}

    def get_loop_var(self, index):
        return self._loop_var.get(index, None)

    def set_loop_var(self, index, value):
        self._loop_var[index] = value


class CallStack:
    """
    The CallStack is initialzed with a root-level StackFrame.

    Prior to a JSR, a CTX command leads to a call to push_stack_frame(), which
    pushes self._top onto the stack and creates a new instance of StackFrame,
    therefore establishing a new context.

    Also prior to the JSR, optional PARAM instructions may place values into the
    current context (self._top) as named variables.

    After the JSR. an END_CTX command pops the top of the stack into self._top.
    """

    def __init__(self):
        self.reset()

    def reset(self) -> None:
        self._top = StackFrame()
        self._top.constants = {}

    def get_top(self) -> StackFrame:
        return self._top

    def new_frame(self):
        self._top = StackFrame(self._top)
        return self._top

    def put_param(self, name, value=None) -> None:
        self._top.params[name] = value

    def enter_routine(self) -> None:
        self._top.vars = self._top.params

    def exit_routine(self) -> None:
        self._top = self._top.parent

    def put_variable(self, index, value) -> None:
        if isinstance(index, LoopVar):
            self._top.set_loop_var(index, value)
        else:
            self._top.put_variable(index, value)

    def put_constant(self, name: str, value) -> None:
        self._top.put_constant(name, value)

    def get_variable(self, index):
        if isinstance(index, LoopVar):
            return self._top.get_loop_var(index)
        return self._top.get_variable(index)

    def set_return(self, address) -> None:
        self._top.return_addr = address

    def get_return(self) -> int:
        return self._top.return_addr

    def get_parameter(self, name):
        return self._top.get_parameter(name)

    def pop_frame(self) -> None:
        self._top = self._top.parent

    def enter_loop(self) -> None:
        self._top = LoopFrame(self._top)

    def exit_loop(self) -> None:
        self._top = self._top.parent

    def unwind_loops(self) -> None:
        while isinstance(self._top, LoopFrame):
            self._top = self.parent
