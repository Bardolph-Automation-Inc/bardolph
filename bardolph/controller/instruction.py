from enum import IntEnum


next_int_value = 0
def auto():
    global next_int_value
    next_int_value += 1
    return next_int_value


class OpCode(IntEnum):
    color = auto()
    end = auto()
    get_color = auto()
    nop = auto()
    pause = auto()
    power = auto()
    set_reg = auto()
    stop = auto()
    time_wait = auto()
    
    
class Operand(IntEnum):
    light = auto()
    group = auto()
    location = auto()


class Instruction:
    def __init__(self, op_code = OpCode.nop, name = None, param = None):
        self.op_code = op_code
        self.name = name
        self.param = param

    def __repr__(self):
        if self.param == None:
            if self.name == None:
                return 'Instruction(OpCode.{}, None, None)'.format(
                    self.op_code.name)
            else:
                return 'Instruction(OpCode.{}, "{}", None)'.format(
                    self.op_code.name, self.name)
        
        if type(self.param).__name__ == 'str':
            param_str = '"{}"'.format(self.param)
        else:
            param_str = str(self.param)
            
        return 'Instruction(OpCode.{}, "{}", {})'.format(
            self.op_code.name, self.name, param_str)
        
    def __eq__(self, other):
        if type(self) == type(other):
            return (self.op_code == other.op_code
                    and self.name == other.name and self.param == other.param)
        else:
            raise TypeError
        
    def as_list_text(self):
        if self.op_code != OpCode.set_reg:
            return 'OpCode.{}'.format(self.op_code.name)
          
        if type(self.param).__name__ == 'str':
            param_str = '"{}"'.format(self.param)
        else:
            param_str = str(self.param)
            
        return 'OpCode.set_reg, "{}", {}'.format(self.name, param_str)
