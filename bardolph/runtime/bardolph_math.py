import builtins
import math
import random as py_random

from bardolph.runtime.bardolph_fn import builtin


@builtin
def round(x):
    return builtins.round(x)

@builtin
def trunc(x):
    return math.trunc(x)

@builtin
def floor(x):
    return math.floor(x)

@builtin
def ceil(x):
    return math.ceil(x)

@builtin
def sqrt(x):
    return math.sqrt(x) if x >= 0.0 else -1

@builtin
def sin(x):
    return math.sin(math.radians(x))

@builtin
def cos(x):
    return math.cos(math.radians(x))

@builtin
def tan(x):
    return math.tan(math.radians(x))

@builtin
def asin(x):
    return math.degrees(math.asin(x))

@builtin
def acos(x):
    return math.degrees(math.acos(x))

@builtin
def atan(x):
    return math.degrees(math.atan(x))

@builtin
def cycle(theta):
    return theta if theta >= 0.0 and theta < 360.0 else theta % 360.0

@builtin
def random(min, max):
    return py_random.randrange(min, max)

def configure():
    py_random.seed()

