from .eval_stack import EvalStack
from .vm_codes import LoopVar, Operand, Operator, Register

from bardolph.controller.i_controller import LightSet
from bardolph.lib.injection import inject, injected, provide
from bardolph.lib.sorted_list import SortedList

class VmDiscover:
    def __init__(self, call_stack, reg):
        self._call_stack = call_stack
        self._reg = reg

    def disc(self, target=None) -> None:
        self._disc(0, self._first_set, target)

    def discl(self, target=None) -> None:
        self._disc(-1, self._last_set, target)

    def _disc(self, index, fn, target) -> None:
        """
        Discover the first light, group, or location matching the criteria.

        If the operand register is light, get the first of all the lights.
        The target parameter is unused in this case.

        If the operand register is group or location:
            If target is Operand.ALL: start traversal of all groups or locations
            If target is a string: start traversal within the group or location
                having that name.
        """
        if self._reg.operand == Operand.LIGHT:
            self._light_or_null(index)
        elif target == Operand.ALL:
            fn()
        else:
            self._member_or_null(target, index)

    @inject(LightSet)
    def _light_or_null(self, index, light_set) -> None:
        """Use index as a subscript into the list of light names. If the
            list is empty or the name is not present, put null into the result
            register. Otherwise, put the light name into the result reg.
        """
        name_list = light_set.light_names
        if len(name_list) == 0:
            self._reg.result = Operand.NULL
        else:
            self._reg.result = name_list[index] or Operand.NULL

    def _first_set(self) -> None:
        name_list = self._names_by_oper()
        self._reg.result = name_list[0] if len(name_list) > 0 else Operand.NULL

    def _last_set(self) -> None:
        name_list = self._names_by_oper()
        self._reg.result = name_list[-1] if len(name_list) > 0 else Operand.NULL

    def _member_or_null(self, name, index) -> None:
        name = self._param_to_value(name)
        name_list = self._set_by_oper(name)
        if name_list is not None and len(name_list) > 0:
            self._reg.result = name_list[index] or Operand.NULL
        else:
            self._reg.result = Operand.NULL

    def discp(self, current, set_name=None) -> None:
        self._discnp(current, set_name, SortedList.prev)

    def discn(self, current, set_name=None) -> None:
        self._discnp(current, set_name, SortedList.next)

    def _discnp(self, current, target, fn) -> None:
        """
        Discover the next or previous light, group, or location matching the
        criteria.

        If the operand register is light, get the subsequent light in the set
        of all lights.

        If the operand register is group or location:
            If target is Operand.ALL: get the subsequent group or location
            If target is a string: get the subsequent light within the group or
                location having that name.
        """
        current = self._param_to_value(current)
        target = self._param_to_value(target)
        if self._reg.operand == Operand.LIGHT or target == Operand.ALL:
            name_list = self._names_by_oper()
        else:
            name_list = self._set_by_oper(target)
        self._reg.result = fn(name_list, current) or Operand.NULL

    def _param_to_value(self, param):
        if isinstance(param, (str, Operand)):
            return param
        if isinstance(param, Register):
            return self._reg.get_by_enum(param)
        return self._call_stack.get_variable(param)

    @inject(LightSet)
    def _set_by_oper(self, name, light_set) -> SortedList:
        if self._reg.operand == Operand.GROUP:
            return light_set.get_group(name)
        elif self._reg.operand == Operand.LOCATION:
            return light_set.get_location(name)
        return None

    @inject(LightSet)
    def _names_by_oper(self, light_set):
        if self._reg.operand == Operand.GROUP:
            return light_set.group_names
        elif self._reg.operand == Operand.LOCATION:
            return light_set.location_names
        return light_set.light_names
