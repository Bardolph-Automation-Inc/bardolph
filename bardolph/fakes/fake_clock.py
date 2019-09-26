from bardolph.lib.i_lib import Clock
from bardolph.lib import injection

def configure():
    """ Bind empty instance to itself; complete no-op. """
    injection.bind(Clock).to(Clock)
