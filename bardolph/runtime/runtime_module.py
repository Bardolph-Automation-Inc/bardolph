import importlib
import inspect

from bardolph.lib.injection import bind_instance
from bardolph.runtime import bardolph_fn, i_runtime


class Runtime(i_runtime.Runtime):
    _module_names = ('bardolph.runtime.bardolph_math',
                     'bardolph.runtime.query')

    def __init__(self):
        modules = [importlib.import_module(name)
                   for name in Runtime._module_names]
        for module in modules:
            module.configure()

        self._fns = {
            name: obj
            for module in modules
            for name, obj in inspect.getmembers(module)
            if bardolph_fn.is_builtin(obj)}

    def get_fns(self) -> dict:
        return self._fns


class NullRuntime(i_runtime.Runtime):
    def get_fns(self) -> dict:
        return {}


class _NullInit():
    @staticmethod
    def configure():
        bind_instance(NullRuntime()).to(i_runtime.Runtime)


def using_null():
    return _NullInit()


def configure():
    bind_instance(Runtime()).to(i_runtime.Runtime)
