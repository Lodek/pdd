from collections import namedtuple
from core import Updater, Signal

updater = Updater()

class Wire:

    """Wire carries a bit of data"""

    def __init__(self, value=0):
        self.bit = value

    def __repr__(self):
        return 'Wire({})'.format(self.bit)


BusEvent = namedtuple('BusEvent', ('signal'))
    
class Bus:

    """The Bus class is an abstraction for a wire or a group of wires. 
Bus connects Terminals. Bus are made up of Wires and  are sliceable.
Slicing a Bus returns a new Bus with the matching wires. Any changes made
to the original Bus propagates to the sliced Bus.
Bus value is given by Signal which gives a higher level API. Two Bus are equal if
their signals are equal"""

    
    def __init__(self, n=1):
        self.wires = [Wire() for _ in range(n)] 

    def __repr__(self):
        return 'Bus({})'.format(self.signal)

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

    def __int__(self):
        sig = 0
        for i, wire in enumerate(self.wires):
            sig |= wire.bit << i
        return sig
    
    @property
    def signal(self):
        """Computes Signal for bus and returns it"""
        return Signal(int(self), len(self))
        
    @signal.setter
    def signal(self, value):
        """Constructs a Signal from value and assigns it to self"""
        bits = Signal(value, len(self)).to_bits()
        for wire, bit in zip(self.wires, bits):
            wire.bit = bit
        event = BusEvent(self)
        updater.notify(event)
            
    @classmethod
    def _from_wires(cls, wires):
        bus = Bus(len(wires))
        bus.wires = wires
        return bus
 

class Terminal:

    """Terminals are how circuit blocks interface.
Terminals are conceptually similar to buffers, its input and output are connected
to distinct buses. The terminal reads the input bus' signal and writes 
that same signal to the output bus. It's possible to use a Terminal as a NOT
gate as well, in which case the output would be the logical negation of the input.
The input and output for every circuit Block is a Terminal.
Optionally, it is possible to toggle whether the output propagates the signal
to the bus or not. If self.connected is tied to GND, then the signal will not propagate
this is analogous to being at a High Impedance."""

    def __init__(self, bus_len = -1, connected=VDD, invert=False):
        self._in_bus = None
        self.out_bus = Bus()
        self.invert = invert
        self.connected = connected
        self.bus_len = bus_len

    @property
    def in_bus(self):
        return self._in_bus

    @in_bus.setter
    def in_bus(self, bus):
        if self.bus_len != -1 and len(bus) != self.bus_len:
            raise ValueError("Bus size incompatible with requirements")
        self._in_bus = bus
        l = len(bus)
        self.out_bus.extend(l)
        
    def propagate(self):
        in_sig = self.in_bus.signal
        if self.connected == VDD:
            self.out_bus.signal = in_sig if not self.invert else in_sig.complement()
        
class Circuit:

    """A circuit follows the classical definition from digital logic,
a black box with inputs outputs and a functional specification. 
A Circuit could be a simple AND gate or it could be a full ALU or even processor."""
    
    def __init__(self, inputs, outputs, connections={}, bubbles=[]):
        self.circuits = []
        self.labels = {'in':inputs, 'out':outputs}
        self.terminals = {label:Terminal() for label in inputs + outputs}
        self.connect(connections)
        self.set_bubbles({bubble : True for bubble in bubbles})
        self._func_spec()

    def set_bubbles(self, bubbles):
        """Expects a dictionary with {terminal_label : Value}
Sets the Terminal associated to the label to Value"""
        for label, value in bubbles.items():
            self.terminals[label].invert = value
            
    def _func_spec(self):
        pass
    
    def connect(self, dic):
        """Used to interface with the external Buses for the circuit block.
Expects Dictionary of the form {label:bus} and attaches 'bus' to  'label'
Terminal external connection for the circuit block.
Ie if Terminal 'label' is an output terminal, connects 'bus' to its output bus and
if 'label' is an input terminal 'bus' will be attached to its in_bus"""
        old_triggers = self.get_triggers()
        for label, bus in dic.items():
            if label in self.labels['in']:
                self.terminals[label].in_bus = bus
            elif label in self.labels['out']:
                self.terminals[label].out_bus = bus
            else:
                raise KeyError('No terminal labeled {} in circuit'.format(label))
        updater.unsubscribe(self, old_triggers)
        updater.subscribe(self, self.get_triggers())

    def get_triggers(self):
        return [self.terminals[label].in_bus for label in self.labels['in']]

    def outputs(self, label):
        return self.terminals[label].out_bus
    
    def output(self):
        """Syntatic sugar for outputs. Useful when circuit has one output
Returns the out_bus for the first out terminal."""
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

    def update(self):
        for label in self.labels['in']:
            self.terminals[label].propate()

class Gate(Circuit):

    """Base class for the basic logic gates"""

    _ops = {'and':Signal.AND, 'or':Signal.OR, 'xor':Signal.XOR}
    
    def __init__(self, operation, connections={}, bubbles=[]):
        inputs = 'a b'.split()
        outputs = ['y']
        self.op = self._ops[operation]
        super().__init__(inputs, outputs, connections, bubbles)

    def _compute(self, a_sig, b_sig):
        result = self.op(a_sig, b_sig)
        return result

    def connect(self, dic):
        super().connect(dic)
        y = Bus(len(self.nodes('a')))
        self.terminals['y'].in_bus = y

    def update(self):
        for label in self.labels['in']:
            self.terminals[label].propagate()
        a_sig = self.nodes['a'].signal
        b_sig = self.nodes['b'].signal
        result = self._compute(a_sig, b_sig)
        self.nodes['y'].signal = result
        for label in self.terminals['out']:
            self.terminals[label].propagate()


class SigGen:

    """A Signal Generator object interacts with a bus and sends signals to it."""
    pass


