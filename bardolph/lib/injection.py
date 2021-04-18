import functools

_providers = {}
injected = None


class UnboundException(Exception):
    def __init__(self, intf):
        super().__init__('No implementation for {}'.format(intf))


class Binder:
    def __init__(self, constructor):
        self._constructor = constructor

    def to(self, interface):
        _providers[interface] = self._constructor


class ObjectBinder:
    def __init__(self, instance):
        self._instance = instance

    def to(self, interface):
        _providers[interface] = lambda: self._instance


def inject(interface):
    def fn_wrapper(fn):
        @functools.wraps(fn)
        def param_wrapper(*args, **kwargs):
            return fn(*args, provide(interface), **kwargs)
        return param_wrapper
    return fn_wrapper


def provide(interface):
    if interface not in _providers:
        msg = "interface {}".format(interface)
        raise UnboundException(msg)
    return _providers[interface]()


def configure():
    global _providers
    _providers.clear()


def bind(implementation):
    return Binder(implementation)


def bind_instance(implementor):
    return ObjectBinder(implementor)
