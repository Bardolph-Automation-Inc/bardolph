class Trace:
    trace_enabled = False
    callback = print

def trace_call(fn):
    def wrapper(*args, **kwargs):
        if Trace.trace_enabled:
            Trace.callback("Calling: {}".format(fn.__name__))
        return fn(*args, **kwargs)
    return wrapper

def trace_call_enable(enable):
    Trace.trace_enabled = enable

def trace_call_callback(callback):
    Trace.callback = callback
