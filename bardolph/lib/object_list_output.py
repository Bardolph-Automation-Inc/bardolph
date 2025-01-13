from bardolph.lib import i_lib
from bardolph.lib.injection import bind

class ObjectListOutput(i_lib.Output):
    def __init__(self):
        self._output_objects = []

    def out(self, output) -> None:
        self._output_objects.append(output)

    def newline(self) -> None:
        self._output_objects.append('\n')

    def flush(self) -> None:
        pass

    def get_object(self) -> object:
        return self._output_objects[0]

    def get_objects(self) -> list:
        return self._output_objects

def configure():
    bind(ObjectListOutput).to(i_lib.Output)
