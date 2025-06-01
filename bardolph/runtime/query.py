from bardolph.controller.i_controller import (
    LightSet, MatrixLight, MultizoneLight)
from bardolph.lib.injection import inject
from bardolph.runtime.bardolph_fn import builtin


class QueryImpl:
    _the_instance = None

    def __init__(self):
        self._fn_table = {
            'is-color': self._is_color,
            'is-matrix': self._is_matrix,
            'is-multizone': self._is_multizone,
            'height': self._height,
            'width': self._width
        }

    @staticmethod
    def configure():
        QueryImpl._the_instance = QueryImpl()

    @staticmethod
    @inject(LightSet)
    def _is_color(name, light_set) -> int:
        light = light_set.get_light(name)
        return 1 if light is not None and light.is_color() else 0

    @staticmethod
    @inject(LightSet)
    def _is_matrix(name, light_set) -> int:
        light = light_set.get_light(name)
        return 1 if light is not None and isinstance(light, MatrixLight) else 0

    @staticmethod
    @inject(LightSet)
    def _is_multizone(name, light_set) -> int:
        light = light_set.get_light(name)
        return 1 if light is not None and isinstance(light, MultizoneLight) else 0

    @staticmethod
    @inject(LightSet)
    def _height(name, light_set) -> int:
        light = light_set.get_light(name)
        return 0 if light is None else light.get_height()

    @staticmethod
    @inject(LightSet)
    def _width(name, light_set) -> int:
        light = light_set.get_light(name)
        return 0 if light is None else light.get_width()

    def query(self, topic, object_name):
        fn = self._fn_table.get(topic, None)
        return fn(object_name) if fn is not None else 0


@builtin
def query(topic, object_name):
    return QueryImpl._the_instance.query(topic, object_name)


def configure():
    QueryImpl.configure()
