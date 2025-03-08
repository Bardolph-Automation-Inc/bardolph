import importlib
import inspect

from bardolph.lib.injection import bind_instance
from bardolph.runtime import bardolph_fn, i_runtime

_module_names = ('bardolph.runtime.bardolph_math', )


class Runtime(i_runtime.Runtime):
    def __init__(self):
        self._fns = {
            name: obj
            for module_name in _module_names
            for name, obj in inspect.getmembers(
                importlib.import_module(module_name))
            if bardolph_fn.is_builtin(obj)}

    def get_fns(self) -> dict:
        return self._fns


def configure():
    bind_instance(Runtime()).to(i_runtime.Runtime)
