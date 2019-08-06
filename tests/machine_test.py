#!/usr/bin/env python3

import unittest

from bardolph.controller.i_controller import LightSet
from bardolph.controller.instruction import Instruction, OpCode, Operand
from bardolph.controller.machine import Machine
from bardolph.lib.injection import provide
from tests import test_module

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
    
    def code_for_get(self, name, operand):
        return [
            Instruction(OpCode.set_reg, "name", name),
            Instruction(OpCode.set_reg, "operand", operand),
            Instruction(OpCode.get_color)
        ]
    
    def test_get_single_color(self):
        program = self.code_for_get(self.names[0], Operand.light)
        machine = Machine()
        machine.run(program)
        self.assertListEqual(machine.color_from_reg(), self.colors[0])

    def test_get_group_color(self):
        program = self.code_for_get("Group1", Operand.group)
        machine = Machine()
        machine.run(program)
        avg = [14, 18, 22, 26]
        self.assertListEqual(machine.color_from_reg(), avg)

    def test_get_location_color(self):
        program = self.code_for_get("Loc2", Operand.location)
        machine = Machine()
        machine.run(program)
        avg = [44, 48, 52, 56]
        self.assertListEqual(machine.color_from_reg(), avg)

    def code_for_set(self, name, operand, params):
        return [
            Instruction(OpCode.set_reg, "hue", params[0]),
            Instruction(OpCode.set_reg, "saturation", params[1]),
            Instruction(OpCode.set_reg, "brightness", params[2]),
            Instruction(OpCode.set_reg, "kelvin", params[3]),
            Instruction(OpCode.set_reg, "name", name),
            Instruction(OpCode.set_reg, "operand", operand),
            Instruction(OpCode.color)
        ]
    
    def test_set_single_color(self):
        color = [1, 2, 3, 4]
        program = self.code_for_set(self.names[0], Operand.light, color)
        machine = Machine()
        machine.run(program)
        self.assertListEqual(machine.color_from_reg(), color)

if __name__ == '__main__':
    unittest.main()
