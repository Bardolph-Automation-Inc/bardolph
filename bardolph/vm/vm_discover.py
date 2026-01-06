from bardolph.controller.i_controller import LightSet
from bardolph.lib.injection import inject
from bardolph.vm.call_stack import CallStack
from bardolph.vm.eval_stack import EvalStack
from bardolph.vm.vm_codes import Operand, Register


class VmDiscover:
    """
    Access to lights by the VM, in support of iterations over collections of
    lights, groups, and/or locations. The direction of the iteration (forward
    or backward) is determined by the the contents of the disc_forward register.
    """
    def __init__(self, call_stack: CallStack, eval_stack: EvalStack, reg):
        self._call_stack = call_stack
        self._eval_stack = eval_stack
        self._reg = reg

    def _push(self, value) -> None:
        self._eval_stack.push(value)

    def _pop(self):
        return self._eval_stack.pop()

    def disc(self) -> None:
        """
        Start the iteration over all lights, all groups, or all locations,
        depending on the contents of the operand register.
        """
        name_list = self._names_for_operand()
        if len(name_list) == 0:
            self._push(Operand.NULL)
        else:
            index = 0 if self._reg.disc_forward else -1
            self._push(name_list[index])

    def discm(self, name) -> None:
        """
        Start the iteration over members of a group or location, depending on
        the contents of the operand register.
        """
        name_list = self._members_of_operand(self._param_to_value(name))
        if name_list and len(name_list) > 0:
            index = 0 if self._reg.disc_forward else -1
            self._push(name_list[index] or Operand.NULL)
        else:
            self._push(Operand.NULL)

    def dnext(self, current) -> None:
        """
        Go to the next object in the iteration.
        """
        name_list = self._names_for_operand()
        current = self._param_to_value(current)
        if self._reg.disc_forward:
            self._push(name_list.next(current) or Operand.NULL)
        else:
            self._push(name_list.prev(current) or Operand.NULL)

    def dnextm(self, name, current) -> None:
        """
        Go to the next object in the iteration over members of a group or
        location.
        """
        name_list = self._members_of_operand(self._param_to_value(name))
        current = self._param_to_value(current)
        if not self._reg.disc_forward:
            self._push(name_list.prev(current) or Operand.NULL)
        else:
            self._push(name_list.next(current) or Operand.NULL)

    def _param_to_value(self, param):
        if isinstance(param, (str, Operand)):
            return param
        if isinstance(param, Register):
            return self._reg.get_by_enum(param)
        return self._call_stack.get_variable(param)

    @inject(LightSet)
    def _members_of_operand(self, name, light_set):
        """
        Get the members of a group or location, as determined by the contents
        of the operand register.
        """
        if self._reg.operand is Operand.GROUP:
            return light_set.get_group_lights(name)
        elif self._reg.operand is Operand.LOCATION:
            return light_set.get_location_lights(name)
        return None

    @inject(LightSet)
    def _names_for_operand(self, light_set):
        """
        Get the names of all the groups, locations, or lights, as determined by
        the contents of the operand register.
        """
        if self._reg.operand is Operand.GROUP:
            return light_set.get_group_names()
        elif self._reg.operand is Operand.LOCATION:
            return light_set.get_location_names()
        assert self._reg.operand is Operand.LIGHT, "incorrect operand"
        return light_set.get_light_names()
