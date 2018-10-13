class Signal:

"""Signal abstracts the individual 0s and 1s of a eletric pulse into a higher level
entity. Signal encodes the information that is sent back and forth in a digital
circuit, it can carry an arbitrary number of bits of data which is defined at 
init time. Signal provides a method that receives a Signal object and returns
a new object which is the logical negation of the former."""
    
    def __init__(self, values):
        self.values = [int(v) for v in values]

    @classmethod
    def zeroes(cls, bits):
        return cls('0'*bits)

    def __len__(self):
        return len(self.values)

    @classmethod
    def NOT(cls, a):
        """Return a new Signal object which is the logical complement for
the current value of self.values"""
        inv = [~v for v in a.values]
        return cls(inv)

    @classmethod
    def OR(cls, a, b):
        res = [i|j for i, j, in zip(a.signal, b.signal)]
        return cls(res)

    @classmethod
    def AND(cls, a, b):
        res = [i&j for i, j, in zip(a.signal, b.signal)]
        return cls(res)

    @classmethod
    def XOR(cls, a, b):
        res = [i^j for i, j, in zip(a.signal, b.signal)]
        return cls(res)

class Bus:

"""The Bus class is an abstraction for a wire or a group of wires. 
Busses are connected to Inputs and Outputs of Terminals.
A Bus can only have a single value at once and though its value can change
its size cannot. The size of a Bus is given by how many bits of information
it can transmit, each bit is analogous to a physical wire on a real circuit"""

    def __init__(self, values):
        self.signal = Signal(values)

    @classmethod
    def from_lines(cls, lines):
        """Alternative init for Bus, instead of receiving the bus value
receives the number of line and init them all to 0, returns new Bus"""
        values = '0'*lines
        return cls(values)

    def __len__(self):
        return len(self.signal)

    
class Terminal:

    """Terminals are how circuit blocks communicate information.
Terminals are conceptually similar to buffers, its input and output are connected
to, distinct, busses. The terminal reads the input bus' signal and writes 
that same signal to the output bus. It's possible to use a Terminal as a NOT
gate as well, in which case the output would be the logical negation of the input.
The input and output for every circuit Block is a Terminal.
Optionally, it is possible to toggle whether the output propagates the signal
to the bus or not. If self.connected is False, then the signal will not propagate
this is analogous to being at a High Impedance."""

    def __init__(self, in_bus, out_bus=None, connected=True, invert=False):
        self.in_bus = in
        self.invert = invert
        self.connected = connected
        self.out_bus = Bus.from_lines(len(in_bus)) if not out_bus else out_bus
        
    def propagate(self):
        in_sig = self.in_bus.signal
        if self.connected:
            self.out_bus.signal = in_sig if not self.invert else in_sig.NOT()
            
    
#    """A Block is a general compoenent of a circuit. Blocks could be a simple AND gate
#    or it could be a full ALU or even processor. Blocks can be made up of blocks.
#    A block is a general combinational logic element, it has inputs, outputs and
#    a functional specification."""
