from collections import OrderedDict

GND = Bus(1)
VDD = Bus(1)
VDD.signal = '1'

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

    def __init__(self, in_bus=None, connected=VDD, invert=False):
        self._in_bus = None
        self.out_bus = None
        if in_bus:
            self.in_bus = in_bus
        self.invert = invert
        self.connected = connected

    @property
    def in_bus(self):
        return self._in_bus

    @in_bus.setter
    def in_bus(self, bus):
        self._in_bus = bus
        l = len(bus)
        self.out_bus = Bus(l)
        
    def propagate(self):
        in_sig = self.in_bus.signal
        if self.connected.signal == Signal('1'):
            self.out_bus.signal = in_sig if not self.invert else in_sig.NOT()
            

class Circuit:

    """A circuit follows the classical definition from digital logic,
a black box with inputs outputs and a functional specification. 
A Circuit could be a simple AND gate or it could be a full ALU or even processor."""
    
    def __init__(self, inputs, outputs, invert=[]):
        self.invert = invert
        self.circuits = []
        self.labels = {'in':inputs, 'out':outputs}
        self.terminals = {label:Terminal() for label in inputs + outputs}
        self._func_spec()


    def _func_spec():
        pass
    
    def connect(self, dic):
        """Dictionary is of the form {label:bus}, sets external connection of
Terminal linked to 'label' to 'bus'"""
        for label, bus in dic.items():
            if label in self.labels['in']:
                self.terminals[label].in_bus = bus
            elif label in self.labels['out']:
                self.terminals[label].out_bus = bus

    def connections(self, label):
        if label in self.labels['in']:
            bus = self.terminals[label].in_bus
        elif label in self.labels['out']:
            bus = self.terminals[label].out_bus
        return bus

    def output(self):
        label = self.labels['out'][0]
        return self.terminals[label].out_bus

    def nodes(self, label):
        """Return Bus associated to internal connection of the Terminal
linked to label"""
        if label in self.labels['in']:
            bus = self.terminals[label].out_bus
        elif label in self.labels['out']:
            bus = self.terminals[label].in_bus
        return bus

    def compute(self):
        for label in self.terminals['in']:
            self.terminals[label].propagate()
        for circuit in self.circuits:
            circuit.compute()
        for label in self.terminals['out']:
            self.terminals[label].propagate()


class Gate(Circuit):

    """Base class for the basic logic gates"""

    _ops = {'and':Signal.AND, 'or':Signal.OR, 'xor':Signal.XOR}
    
    def __init__(self, a, b, operation, invert=[]):
        inputs = 'a b'.split()
        outputs = ['y']
        self.op = self._ops[operation]
        super().__init__(inputs, outputs, invert)

    def _func_spec(self, a_sig, b_sig):
        result = self.op(a_sig, b_sig)
        return result
        
    def compute(self):
        for label in self.terminals['in']:
            self.terminals[label].propagate()
        a_sig = self.nodes['a'].signal
        b_sig = self.nodes['b'].signal
        result = self._func_spec(a_sig, b_sig)
        self.nodes['y'].signal = result
        for label in self.terminals['out']:
            self.terminals[label].propagate()

        
class Clock:
    pass
