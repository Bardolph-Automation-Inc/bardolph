_next_int_value = -1

def auto():
    global _next_int_value
    _next_int_value += 1
    return _next_int_value
