from enum import IntEnum
import logging

from ..lib.i_lib import Clock
from ..lib.color import average_color
from ..lib.injection import inject, provide

from .get_key import getch
from .i_controller import LightSet
from .instruction import OpCode, Operand


class Registers:
    def __init__(self):
        self.hue = 0
        self.saturation = 0
        self.brightness = 0
        self.kelvin = 0
        self.duration = 0
        self.power = False
        self.name =  None
        self.operand = None
        self.time = 0 # ms.

    def get_color(self):
        return [self.hue, self.saturation, self.brightness, self.kelvin]

        
class Machine:
    def __init__(self):
        self.pc = 0
        self.cue_time = 0
        self.clock = provide(Clock)
        self.variables = {}
        self.program = []
        self.reg = Registers()
        self.enable_pause = True
        self.fn_table = {
            OpCode.color: self.color,
            OpCode.end: self.end,
            OpCode.get_color: self.get_color,
            OpCode.nop: self.nop,
            OpCode.pause: self.pause,
            OpCode.power: self.power,
            OpCode.set_reg: self.set_reg,
            OpCode.stop: self.stop,
            OpCode.time_wait: self.time_wait
        }

    def run(self, program):
        self.program = program
        self.pc = 0
        self.cue_time = 0  
        self.clock.start()
        while self.pc < len(self.program):
            inst = self.program[self.pc]
            if inst.op_code == OpCode.stop:
                break
            self.fn_table[inst.op_code]()
            self.pc += 1
        self.clock.stop()

    def apply_to(self, get_fn, op_fn):
        lst_or_obj = get_fn(self.reg.name)
        if lst_or_obj is not None:
            try:
                for light in lst_or_obj:
                    op_fn(light)
            except TypeError:
                op_fn(lst_or_obj)

    def color(self): {
            Operand.light: self.color_light, 
            Operand.group: self.color_group,
            Operand.location: self.color_location
        }[self.reg.operand]()

    @inject(LightSet)
    def color_light(self, light_set):
        if self.reg.name is None:
            light_set.set_color(self.reg.get_color(), self.reg.duration)
        else:
            self.apply_to(self.one_light, self.light_command)
    
    @inject(LightSet)
    def color_group(self, light_set):
        self.apply_to(light_set.get_group, self.light_command)
        
    @inject(LightSet)
    def color_location(self, light_set):
        self.apply_to(light_set.get_location, self.light_command)
        
    def light_command(self, target):
        """ target is lifxlan.light.Light """
        target.set_color(self.reg.get_color(), self.reg.duration, True)
                                                   
    def light_set_command(self, target):
        """ target is lib.i_lib.LightSet. """
        target.set_color(self.reg.get_color(), self.reg.duration)
                                                   
    @inject(LightSet)
    def one_light(self, name, light_set):
        light = light_set.get_light(name)
        if light is None:
            self.report_missing(name)
            return None
        else:
            return light
        
    def power(self): { 
        Operand.light: self.power_light, 
        Operand.group: self.power_group,
        Operand.location: self.power_location
    }[self.reg.operand]()
    
    @inject(LightSet)
    def power_light(self, light_set):
        if self.reg.name is None:
            light_set.set_power(self.power_param(), self.reg.duration)
        else:
            self.apply_to(self.one_light, self.power_command)
                
    @inject(LightSet)
    def power_group(self, light_set):
        self.apply_to(light_set.get_group, self.power_command)
        
    @inject(LightSet)
    def power_location(self, light_set):
        self.apply_to(light_set.get_location, self.power_command)           

    def power_command(self, target):
        """ target can be lifxlan.light.Light or lib.i_lib.LightSet. """
        target.set_power(self.power_param(), self.reg.duration)

    def get_color(self): { 
        Operand.light: self.get_light_color, 
        Operand.group: self.get_group_color,
        Operand.location: self.get_location_color
    }[self.reg.operand]()
    
    @inject(LightSet)
    def get_light_color(self, light_set):
        if self.reg.name is None:
            self.get_average_color(light_set.get_all_lights)
        else:
            light = light_set.get_light(self.reg.name)
            if light is None:
                self.report_missing(self.reg.name)
            else:
                self.color_to_reg(light.get_color())

    @inject(LightSet)
    def get_group_color(self, light_set):
        self.get_average_color(light_set.get_group)
        
    @inject(LightSet)
    def get_location_color(self, light_set):
        self.get_average_color(light_set.get_location)
    
    def get_average_color(self, get_fn):
        if self.reg.name is None:
            colors = [light.get_color() for light in get_fn()]
        else:
            colors = get_fn(self.reg.name)
        self.color_to_reg(average_color(colors))
            
    def nop(self): pass
        
    def pause(self):
        if self.enable_pause:
            print("Press any to continue, q to quit, ! to run.")
            c = getch()
            if c == 'q':
                self.stop()
            else:
                print("Running...")
                if c == '!':
                    self.enable_pause = False
            
    def check_wait(self):
        time = self.reg.time
        if time > 0:
            self.clock.pause_for(time / 1000.0)

    def end(self):
        self.stop()

    def stop(self):
        self.pc = len(self.program)
    
    def set_reg(self):
        inst = self.program[self.pc]
        setattr(self.reg, inst.name, inst.param)
        
    def time_wait(self):
        self.check_wait()
          
    def report_missing(self, name):
        logging.warning("Light \"{}\" not found.".format(name))

    def power_param(self):
        return 65535 if self.reg.power else 0
        
    def color_from_reg(self):
        return [self.reg.hue, self.reg.saturation, self.reg.brightness,
            self.reg.kelvin]

    def color_to_reg(self, color):
        if color != None:
            r = self.reg
            r.hue, r.saturation, r.brightness, r.kelvin = color
