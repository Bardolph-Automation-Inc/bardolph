import functools


def noneable(fn):
    # If any incoming parameter is None, return None. Otherwise, call the
    # function.
    @functools.wraps(fn)
    def none_to_none(*args, **kwargs):
        if None in args or None in kwargs.values():
            return None
        return fn(*args, **kwargs)
    return none_to_none
