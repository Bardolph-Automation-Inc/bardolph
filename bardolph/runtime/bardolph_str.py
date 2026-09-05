from bardolph.runtime.bardolph_fn import builtin


@builtin
def concat(str0, str1):
    return str(str0) + str(str1)

@builtin
def left(s, num_chars):
    return s[0:num_chars]

@builtin
def right(s, num_chars):
    return s[len(s) - num_chars:]

@builtin
def substr(s, first, length):
    return s[first:first + length]

@builtin
def contains(s, search_for):
    return 1 if search_for in s else 0

@builtin
def length(s):
    return len(s)

def configure():
    pass
