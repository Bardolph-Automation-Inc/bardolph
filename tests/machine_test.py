#!/usr/bin/env python3

import unittest

from bardolph.controller.instruction import Instruction
from bardolph.controller.instruction import OpCode, Operand, Register
from bardolph.controller import i_controller
from bardolph.controller.machine import Machine
from bardolph.controller.units import UnitMode
from bardolph.lib.injection import provide


from . import test_module

class MachineTest(unittest.TestCase):
    def setUp(self):
        test_module.configure()

        self._group0 = 'Group 0'
        self._group1 = 'Group 1'
        
        self._location0 = 'Location 0'
        self._location1 = 'Location 1'
                
        self._colors = [
            [4, 8, 12, 16], [24, 28, 32, 36], [44, 48, 52, 56], [64, 68, 72, 76]
        ]
        self._names = [
            "Test g1 l1", "Test g1 l2", "Test g2 l1", "Test g2 l2"
        ]        

        lifx = provide(i_controller.Lifx)
        lifx.init_from([
            (self._names[0], self._group0, self._location0, self._colors[0]),  
            (self._names[1], self._group0, self._location1, self._colors[1]),
            (self._names[2], self._group1, self._location0, self._colors[2]),
            (self._names[3], self._group1, self._location1, self._colors[3])
        ])
        light_set = provide(i_controller.LightSet)
        light_set.discover()
        
    @classmethod
    def code_for_get(cls, name, operand):
        return [
            Instruction(OpCode.SET_REG, Register.NAME, name),
            Instruction(OpCode.SET_REG, Register.OPERAND, operand),
            Instruction(OpCode.GET_COLOR)
        ]

    @classmethod
    def code_for_set(cls, name, operand, params):
        return [
            Instruction(OpCode.SET_REG, Register.UNIT_MODE, UnitMode.RAW),
            Instruction(OpCode.SET_REG, Register.HUE, params[0]),
            Instruction(OpCode.SET_REG, Register.SATURATION, params[1]),
            Instruction(OpCode.SET_REG, Register.BRIGHTNESS, params[2]),
            Instruction(OpCode.SET_REG, Register.KELVIN, params[3]),
            Instruction(OpCode.SET_REG, Register.NAME, name),
            Instruction(OpCode.SET_REG, Register.OPERAND, operand),
            Instruction(OpCode.COLOR)
        ]

    def test_get_color(self):
        program = MachineTest.code_for_get(self._names[0], Operand.LIGHT)
        machine = Machine()
        machine.run(program)
        self.assertTrue(machine.color_from_reg(), self._colors[0])

    def test_set_single_color(self):
        color = [1, 2, 3, 4]
        name = self._names[0]
        
        program = MachineTest.code_for_set(name, Operand.LIGHT, color)
        machine = Machine()
        machine.run(program)
        self.assertListEqual(machine.color_from_reg(), color)
        light_set = provide(i_controller.LightSet)
        light = light_set.get_light(name)._impl
        self.assertTrue(light.was_set(color))

if __name__ == '__main__':
    unittest.main()
