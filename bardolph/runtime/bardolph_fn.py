import functools
import inspect


_PARAMS = 'bardolph_params'


def builtin(fn):
    sig = inspect.signature(fn)
    setattr(fn, _PARAMS, [name for name in sig.parameters.keys()])

    @functools.wraps(fn)
    def wrapper(*args):
        stack_frame = args[0]
        param_names = params(fn)
        actual_params = [
            stack_frame.get_parameter(name) for name in param_names]
        return fn(*actual_params)
    return wrapper


def is_builtin(obj):
    return hasattr(obj, _PARAMS) if inspect.isfunction(obj) else False


def params(fn):
    return getattr(fn, _PARAMS) if hasattr(fn, _PARAMS) else []
