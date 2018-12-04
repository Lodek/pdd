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
        """Changes size of self to size, new Wires are initialized to 0"""
        nsize = size - len(self)
        if nsize > 0:
            self.wires += [Wire() for _ in range(nsize)]
        else:
            self.wires = self.wires[:size]

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
 
