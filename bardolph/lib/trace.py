class Trace:
    trace_enabled = False
    callback = print

def trace_call(fn):
    def wrapper(*args, **kwargs):
        if not Trace.trace_enabled:
            return fn(*args, **kwargs)

        Trace.callback("Enter: {}".format(fn.__name__))
        result = fn(*args, **kwargs)
        Trace.callback("Exit: {}".format(fn.__name__))
        return result
    return wrapper

def trace_call_enable(enable):
    Trace.trace_enabled = enable

def trace_call_callback(callback):
    Trace.callback = callback
