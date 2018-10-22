from collections import OrderedDict

GND = 0
VDD = 1

class Signal:

    """Signal provies an API to deal with digital signals. The data carried by
a Bus is encoded as a Signal. Signal provides methods to perform logical operations
that takes Signal objects as operands and return a new instace of Signal.
Signal is constructed from an iterable that made of 0 and 1. eg. Signal('0101')"""
    
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

    def complement(self):
        return Signal.NOT(self)

    @classmethod
    def from_wires(cls, wires):
        data = [w.bit for w in wires]
        return cls(data)
        
    @classmethod
    def NOT(cls, a):
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

    """A Bus has a number of Wires, each Wire carries a bit of data"""
    
    def __init__(self, value=0):
        self.bit = value

    def __repr__(self):
        return 'Wire({})'.format(self.bit)

class Bus:

    """The Bus class is an abstraction for a wire or a group of wires. 
Bus connects Terminals. Bus are made up of Wires therefore they are sliceable,
slicing a Bus returns a new Bus that is associated to the previosu one. Any
changes made to the original Bus propagates to the sliced Bus.
Bus value is given by Signal which gives a higher level API. Two Bus are equal if
their signals are equal"""

    def __init__(self, n=1):
        self.wires = [Wire() for _ in range(n)] 

    def __repr__(self):
        return 'Bus({})'.format(repr(self.signal))

    def __len__(self):
        return len(self.wires)

    def __getitem__(self, index):
        """Creates a new Bus from the sliced wires, returns new Bus"""
        wires = self.wires[index]
        if type(wires) != list:
            wires = [wires]
        return Bus._from_wires(wires)

    def __eq__(self, other):
        return True if self.signal == other.signal else False

    def extend(self, size):
        """Changes size of self to size, new Wires are initialized to 0"""
        nsize = size - len(self)
        if nsize > 0:
            self.wires += [Wire() for _ in range(nsize)]
        else:
            self.wires = self.wires[:size]
        
    @property
    def signal(self):
        """Computes Signal for bus and returns it"""
        return Signal.from_wires(self.wires)
        
    @signal.setter
    def signal(self, value):
        """Constructs a Signal from value and assigns it to self"""
        s = Signal(value)
        if len(s) != len(self):
            raise ValueError('Value has the wrong length')
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

    def __init__(self, max_bus = -1, connected=VDD, invert=False):
        self._in_bus = None
        self.out_bus = Bus()
        self.invert = invert
        self.connected = connected
        self.max_bus = max_bus

    @property
    def in_bus(self):
        return self._in_bus

    @in_bus.setter
    def in_bus(self, bus):
        if self.bus_requirement != -1 and len(bus) != self.bus_requirement:
            raise ValueError("Bus size incompatible with requirements")
        self._in_bus = bus
        l = len(bus)
        self.out_bus.extend(l)
        
    def propagate(self):
        in_sig = self.in_bus.signal
        if self.connected.signal == VDD:
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
        for label in self.invert:
            self.terminals[label].invert = True

    def _func_spec():
        pass
    
    def connect(self, dic):
        """Dictionary is of the form {label:bus}, attaches 'bus' to  'label' Terminal's in_bus"""
        for label, bus in dic.items():
            self.terminals[label].in_bus = bus

    def outputs(self, label):
        return self.terminals[label].out_bus
    
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


    def connect(self, dic):
        super().connect(dic)
        b = Bus(len(self.nodes['a']))
        self.connect({'y':b})


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
