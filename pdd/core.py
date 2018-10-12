
class Port:

    """Port provides an abstraction for an input or output in digital logic.
    Each port is connected to a single Bus. If port is an output, it propagates it's value
    onto the bus otherwise it receives it's value from the Bus.
    A port can be at a 0 or 1 if connected. If not connected it signifies a 
    High Impedance (Z).
    Ports can be in or out, 0 for 0ut 1 for 1n"""

    IN = 1
    OUT = 0
    
    def __init__(self):
        self.connected = True
        self.bus = None
        self.direction = 

    @property
    def signal(self):
        return self.bus.values

    @signal.setter
    def signal(self, value):
        if self.direction == self.OUT:
            self.bus.signal = value
        else:
            raise AttributeError("Error: IN Port cannot receive signal assignment")

class Block:

    """A Block is a general compoenent of a circuit. Blocks could be a simple AND gate
    or it could be a full ALU or even processor. Blocks can be made up of blocks.
    A block is a general combinational logic element, it has inputs, outputs and
    a functional specification."""
    
    def __init__(self):
        self.inputs = {}
        self.outputs = {}
        self.LUT = {}
        self.blocks = []
        
    def func_spec(self):
        pass

    def _gen_LUT(self):
        pass

class Bus:

    """The Bus class is an abstraction for a wire or a group of wires.
    Buses are measured in lines, each line is an individual wire"""

    def __init__(self, lines, values):
        self.lines = int(lines)
        self.values = [values]
        
