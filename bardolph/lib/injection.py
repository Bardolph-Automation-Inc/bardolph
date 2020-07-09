class UnboundException(Exception):
    def __init__(self, intf):
        super().__init__('No implementation for {}'.format(intf))

class Injection:
    providers = {}

injected = None

class Binder:
    """ Parameter implementation is a class to be used as the factory. """
    def __init__(self, implementation):
        self._implementation = implementation

    def to(self, interface):
        Injection.providers[interface] = self._implementation


class ObjectBinder:
    """ Singleton. Parameter implementor is always returned. """
    def __init__(self, implementor):
        self._implementor = implementor

    def to(self, interface):
        Injection.providers[interface] = lambda: self._implementor


def inject(*interfaces):
    def fn_wrapper(fn):
        def param_wrapper(*args):
            injected_args = []
            for interface in interfaces:
                if interface in Injection.providers:
                    obj = Injection.providers[interface]()
                else:
                    obj = interface()
                injected_args.append(obj)
            args = args + tuple(injected_args)
            return fn(*args)
        return param_wrapper
    return fn_wrapper


def provide(interface):
    if interface not in Injection.providers:
        msg = "interface {}".format(interface)
        raise UnboundException(msg)

    creator = Injection.providers[interface]
    return creator()


def configure(): Injection.providers = {}

def bind(implementation): return Binder(implementation)

def bind_instance(implementor): return ObjectBinder(implementor)
