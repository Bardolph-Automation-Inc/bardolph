from .eval_stack import EvalStack
from .vm_codes import LoopVar, Operand, Operator, Register

from bardolph.controller.i_controller import LightSet
from bardolph.lib.injection import inject, injected, provide
from bardolph.lib.sorted_list import SortedList

class VmDiscover:
    def __init__(self, call_stack, reg):
        self._call_stack = call_stack
        self._reg = reg

    def disc(self) -> None:
        name_list = self._names_by_oper()
        if len(name_list) == 0:
            self._reg.result = Operand.NULL
        else:
            index = 0 if self._reg.disc_forward else -1
            self._reg.result = name_list[index]

    def discm(self, name) -> None:
        name_list = self._set_by_oper(self._param_to_value(name))
        if name_list and len(name_list) > 0:
            index = 0 if self._reg.disc_forward else -1
            self._reg.result = name_list[index] or Operand.NULL
        else:
            self._reg.result = Operand.NULL

    def dnext(self, current) -> None:
        name_list = self._names_by_oper()
        current = self._param_to_value(current)
        if not self._reg.disc_forward:
            self._reg.result = name_list.prev(current) or Operand.NULL
        else:
            self._reg.result = name_list.next(current) or Operand.NULL

    def dnextm(self, name, current) -> None:
        name_list = self._set_by_oper(self._param_to_value(name))
        current = self._param_to_value(current)
        if not self._reg.disc_forward:
            self._reg.result = name_list.prev(current) or Operand.NULL
        else:
            self._reg.result = name_list.next(current) or Operand.NULL

    def _param_to_value(self, param):
        if isinstance(param, (str, Operand)):
            return param
        if isinstance(param, Register):
            return self._reg.get_by_enum(param)
        return self._call_stack.get_variable(param)

    @inject(LightSet)
    def _set_by_oper(self, name, light_set):
        if self._reg.operand is Operand.GROUP:
            return light_set.get_group(name)
        elif self._reg.operand is Operand.LOCATION:
            return light_set.get_location(name)
        return None

    @inject(LightSet)
    def _names_by_oper(self, light_set):
        if self._reg.operand is Operand.GROUP:
            return light_set.group_names
        elif self._reg.operand is Operand.LOCATION:
            return light_set.location_names
        assert self._reg.operand is Operand.LIGHT
        return light_set.light_names
