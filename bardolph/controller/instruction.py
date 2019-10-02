from enum import auto, Enum


class OpCode(Enum):
    COLOR = auto()
    END = auto()
    GET_COLOR = auto()
    NOP = auto()
    PAUSE = auto()
    POWER = auto()
    SET_REG = auto()
    STOP = auto()
    TIME_WAIT = auto()
    
    
class Operand(Enum):
    LIGHT = auto()
    GROUP = auto()
    LOCATION = auto()


class Instruction:
    def __init__(self, op_code = OpCode.NOP, name = None, param = None):
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
        if self.op_code != OpCode.SET_REG:
            return 'OpCode.{}'.format(self.op_code.name)
          
        if type(self.param).__name__ == 'str':
            param_str = '"{}"'.format(self.param)
        else:
            param_str = str(self.param)
            
        return 'OpCode.set_reg, "{}", {}'.format(self.name, param_str)
