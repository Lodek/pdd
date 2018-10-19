from collections import OrderedDict

GND = Bus(1)
VDD = Bus(1)
VDD.signal = 1

class Signal:

    """Signal abstracts the individual 0s and 1s of a eletric pulse into a higher level
entity. Signal encodes the information that is sent back and forth in a digital
circuit, it can carry an arbitrary number of bits of data which is defined at 
init time. Signal provides a methods that perform the standard logical operations
in two instances of SIgnal and returns a new object"""
    
    def __init__(self, data):
        self.data = [int(d) for d in data]

    def __getitem__(self, index):
        return self.data[index]
    
    def __len__(self):
        return len(self.data)

    def __eq__(self, other):
        return True if self.data == other.data else False

    def __repr__(self):
        return 'Signal({})'.format(self.data)
        
    @classmethod
    def from_wires(cls, wires):
        data = [w.bit for w in wires]
        return cls(data)
        
    @classmethod
    def zeroes(cls, bits):
        return cls('0'*bits)

    def complement(self):
        return Signal.NOT(self)

    @classmethod
    def NOT(cls, a):
        """Return a new Signal object which is the logical complement for
the current value of self.data"""
        inv = [1 if v == 0 else 0 for v in a.data]
        return cls(inv)

    @classmethod
    def OR(cls, a, b):
        res = [i|j for i, j, in zip(a.data, b.data)]
        return cls(res)

    @classmethod
    def AND(cls, a, b):
        res = [i&j for i, j, in zip(a.data, b.data)]
        return cls(res)

    @classmethod
    def XOR(cls, a, b):
        res = [i^j for i, j, in zip(a.data, b.data)]
        return cls(res)


class Wire:
    def __init__(self, value=0):
        self.bit = value

    def __repr__(self):
        return 'Wire({})'.format(self.bit)

    def __len__(self):
        return 1
    
class Bus:

    """The Bus class is an abstraction for a wire or a group of wires. 
Busses are connected to Inputs and Outputs of Terminals.
A Bus can only have a single value at once and though its value can change
its size cannot. The size of a Bus is given by how many bits of information
it can transmit, each bit is analogous to a physical wire on a real circuit"""

    def __init__(self, n=1):
        self.wires = [Wire() for _ in range(n)] 

    def __repr__(self):
        return 'Bus({})'.format(repr(self.signal))

    def __len__(self):
        return len(self.wires)

    def __getitem__(self, index):
        return Bus._from_wires(self.wires[index])
    
    @property
    def signal(self):
        return Signal.from_wires(self.wires)
        
    @signal.setter
    def signal(self, value):
        s = Signal(value)
        for wire, d in zip(self.wires, s.data):
            wire.bit = d

    @classmethod
    def _from_wires(cls, wires):
        bus = Bus(len(wires))
        bus.wires = wires
        return bus
    
        
class Terminal:

    """Terminals are how circuit blocks interface.
Terminals are conceptually similar to buffers, its input and output are connected
to distinct busses. The terminal reads the input bus' signal and writes 
that same signal to the output bus. It's possible to use a Terminal as a NOT
gate as well, in which case the output would be the logical negation of the input.
The input and output for every circuit Block is a Terminal.
Optionally, it is possible to toggle whether the output propagates the signal
to the bus or not. If self.connected is tied to GND, then the signal will not propagate
this is analogous to being at a High Impedance."""

    def __init__(self, in_bus, out_bus=None, connected=VDD, invert=False):
        self.in_bus = in_bus
        self.invert = invert
        self.connected = connected
        self.out_bus = Bus.from_lines(len(in_bus)) if not out_bus else out_bus
        
    def propagate(self):
        in_sig = self.in_bus.signal
        if self.connected:
            self.out_bus.signal = in_sig if not self.invert else in_sig.NOT()
            

class Circuit:

    """A circuit follows the classical definition from digital logic,
a black box with inputs outputs and a functional specification. 
A Circuit could be a simple AND gate or it could be a full ALU or even processor."""
    
    def __init__(self, inputs_bus, outputs_bus, invert=[]):
        self.gates = OrderedDict()
        self.terminals = {'in':{}, 'out':{}}
        for label, bus in inputs_bus.items():
            self.terminals['in'][label] = Terminal(bus)
            sample_bus = bus
        for label, bus in outputs_bus.items():
            real_bus = bus if bus else Bus.from_lines(sample_bus)
            self.terminals['out'][label] = Terminal(real_bus)
        

    def nodes(self, group, label):
        if group == 'in':
            return self.terminals[group][label].out_bus
        elif group == 'out':
            return self.terminals[group][label].in_bus
        else:
            return None

    def set_nodes(self, group, label, value):
        if group == 'in':
            self.terminals[group][label].out_bus = value
        elif group == 'out':
            self.terminals[group][label].in_bus = value
            
    def compute(self):
        for terminal in self.terminals['in'].values():
            terminal.propagate()
        for gate in self.gates.values():
            gate.compute()
        for terminal in self.terminals['out'].values():
            terminal.propagate()

    @property
    def inputs(self):
        return {label : term.in_bus for label, term in self.terminals['in'].items()}

    @property
    def outputs(self):
        return {label : term.out_bus for label, term in self.terminals['out'].items()}
        
class Gate(Circuit):

    """Base class for the basic logic gates"""

    _ops = {'and':Signal.AND, 'or':Signal.OR, 'xor':Signal.XOR}
    
    def __init__(self, a, b, operation, out_bus=None, invert=[]):
        inputs_bus = {'a':a, 'b':b}
        outputs_bus = {'y':out_bus}
        for i in invert:
            self.terminals['in'][i].invert = True
        output_in_bus = Bus.from_lines(len(inputs_bus[0]))
        self.terminals['out'] = Terminal(output_in_bus)
        self.op = self._ops[operation]

    @property
    def inputs(self):
        return [term.in_bus for term in self.terminals['in']]

    @property
    def output(self):
        return self.terminals['out'].out_bus
        
    def _func_spec(self):
        result = self.inputs[0].output()
        for terminal in self.inputs[1:]:
            result = self.op(result, temrinal.output())
        return result
        
    def compute(self):
        output = self._func_spec()
        self.output.in_bus.signal = output
        self.output.propagate()

        
class Clock:
    pass
