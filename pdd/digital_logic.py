from collections import namedtuple
from core import Updater, Signal
import logging

updater = Updater() #module wide declartion of Updater
logger = logging.getLogger(__name__)

class Wire:

    """Wire carries a bit of data"""

    def __init__(self, value=0):
        self.bit = value

    def __repr__(self):
        return 'Wire({})'.format(self.bit)


BusEvent = namedtuple('BusEvent', ('signal'))
    
class Bus:

    """The Bus class is an abstraction for a wire or a group of wires. 
Bus connects Terminals. Bus are made up of Wires and are sliceable.
Slicing a Bus returns a new Bus with the matching wires. Any changes made
to the original Bus propagates to the sliced Bus.
Bus value is given by Signal which gives a higher level API. Two Bus are equal if
their signals are equal"""

    def __init__(self, n=1, signal=0):
        self.wires = [Wire() for _ in range(n)]
        self.signal = signal
        logger.debug("New {}".format(repr(self)))

    def __repr__(self):
        return 'Bus({}, n={})'.format(self.signal, len(self))

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
    
    def __int__(self):
        sig = 0
        for i, wire in enumerate(self.wires):
            sig |= wire.bit << i
        return sig

    def extend(self, size):
        """Changes the number of wires in the bus, new Wires are initialized to 0"""
        nsize = size - len(self)
        if nsize > 0:
            self.wires += [Wire() for _ in range(nsize)]
        else:
            self.wires = self.wires[:size]

    @property
    def signal(self):
        """Returns Signal object for bus"""
        return Signal(int(self), len(self))
        
    @signal.setter
    def signal(self, value):
        """ Assigns a new Signal to the bus and notifies the updater"""
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
 
VDD = Bus(1, 1)
GND = Bus()
    
class Terminal:

    """Terminals makes the transition between inside and outside a circuit.
Terminals are conceptually similar to buffers, its input and output are connected
to distinct buses. The terminal reads the input bus' signal and writes 
that same signal to the output bus. It's possible to use a Terminal as a NOT
gate as well, in which case the output would be the logical negation of the input.
The input and output for every circuit Block is a Terminal.
Optionally, it is possible to toggle whether the output propagates the signal
to the bus or not. If self.connected is tied to GND, then the signal will not propagate
this is analogous to being at a High Impedance."""

    def __init__(self, bus_rule=0, connected=VDD, invert=False):
        self._in_bus = None
        self.out_bus = Bus()
        self.bus_rule = bus_rule
        self.invert = invert
        self.connected = connected

    @property
    def in_bus(self):
        return self._in_bus

    @in_bus.setter
    def in_bus(self, bus):
        if len(bus) != self.bus_rule and bus_rule != 0:
            #BusError class?
            raise ValueError("Bus size incompatible with requirements")
        self._in_bus = bus
        l = len(bus)
        self.out_bus.extend(l)
        
    def propagate(self):
        in_sig = self.in_bus.signal
        if self.connected == VDD:
            self.out_bus.signal = in_sig if not self.invert else in_sig.complement()
