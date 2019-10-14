#!/usr/bin/env python3

import unittest

from bardolph.controller.i_controller import LightSet
from bardolph.controller.instruction import Instruction, OpCode, Operand
from bardolph.controller.machine import Machine
from bardolph.lib.injection import provide

from . import test_module

class MachineTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()

        self.light_set = provide(LightSet)
        self.light_set.clear_lights()
        self.colors = [
            [4, 8, 12, 16], [24, 28, 32, 36], [44, 48, 52, 56], [64, 68, 72, 76]
        ]
        self.names = [
            "Test g1 l1", "Test g1 l2", "Test g2 l1", "Test g2 l2"
        ]
        self.light_set.add_light(
            self.names[0], "Group1", "Loc1", self.colors[0])
        self.light_set.add_light(
            self.names[1], "Group1", "Loc2", self.colors[1])
        self.light_set.add_light(
            self.names[2], "Group2", "Loc1", self.colors[2])
        self.light_set.add_light(
            self.names[3], "Group2", "Loc2", self.colors[3])

    @classmethod
    def code_for_get(cls, name, operand):
        return [
            Instruction(OpCode.SET_REG, "name", name),
            Instruction(OpCode.SET_REG, "operand", operand),
            Instruction(OpCode.GET_COLOR)
        ]

    def test_get_single_color(self):
        program = MachineTest.code_for_get(self.names[0], Operand.LIGHT)
        machine = Machine()
        machine.run(program)
        self.assertListEqual(machine.color_from_reg(), self.colors[0])

    def test_get_group_color(self):
        program = MachineTest.code_for_get("Group1", Operand.GROUP)
        machine = Machine()
        machine.run(program)
        avg = [14, 18, 22, 26]
        self.assertListEqual(machine.color_from_reg(), avg)

    def test_get_location_color(self):
        program = MachineTest.code_for_get("Loc2", Operand.LOCATION)
        machine = Machine()
        machine.run(program)
        avg = [44, 48, 52, 56]
        self.assertListEqual(machine.color_from_reg(), avg)

    @classmethod
    def code_for_set(cls, name, operand, params):
        return [
            Instruction(OpCode.SET_REG, "hue", params[0]),
            Instruction(OpCode.SET_REG, "saturation", params[1]),
            Instruction(OpCode.SET_REG, "brightness", params[2]),
            Instruction(OpCode.SET_REG, "kelvin", params[3]),
            Instruction(OpCode.SET_REG, "name", name),
            Instruction(OpCode.SET_REG, "operand", operand),
            Instruction(OpCode.COLOR)
        ]

    def test_set_single_color(self):
        color = [1, 2, 3, 4]
        program = MachineTest.code_for_set(self.names[0], Operand.LIGHT, color)
        machine = Machine()
        machine.run(program)
        self.assertListEqual(machine.color_from_reg(), color)

if __name__ == '__main__':
    unittest.main()
