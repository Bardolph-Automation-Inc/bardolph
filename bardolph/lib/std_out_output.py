from bardolph.lib import i_lib
from bardolph.lib.injection import bind

class StdOutOutput(i_lib.Output):
    def __init__(self):
        self._line_pending = False

    def out(self, output):
        if self._line_pending:
            print(' ', end='')

        self._line_pending = True
        print(output, end='')

    def newline(self):
        print()
        self._line_pending = False

    def flush(self):
        if self._line_pending:
            self.newline()

def configure():
    bind(StdOutOutput).to(i_lib.Output)

