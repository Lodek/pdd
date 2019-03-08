from collections import namedtuple
from core import Updater, Signal
import logging

updater = Updater() #module wide declartion of Updater
logger = logging.getLogger(__name__)

class Wire:
    """
    Wire carries a bit of data
    """
    def __init__(self, value=0):
        self.bit = value

    def __repr__(self):
        return 'Wire({})'.format(self.bit)


    
class Bus:
    """
    The Bus class is an abstraction for a wire or a group of wires. 
    Bus connects Terminals. Bus are made up of Wires and are sliceable.
    Slicing a Bus returns a new Bus with the matching wires. Any changes made
    to the original Bus propagates to the sliced Bus.
    Bus value is given by Signal which gives a higher level API. Two Bus are equal if
    their signals are equal
    """
    BusEvent = namedtuple('BusEvent', ('signal'))

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
        if type(value) == Signal:
            bits = value.to_bits()
        else:
            bits = Signal(value, len(self)).to_bits()
        for wire, bit in zip(self.wires, bits):
            wire.bit = bit
        event = self.BusEvent(self)
        updater.notify(event)
            
    @classmethod
    def _from_wires(cls, wires):
        bus = Bus(len(wires))
        bus.wires = wires
        return bus
 
    
class Terminal:
    """
    Terminals are the door between the outside world and a circuit.

    Terminals are conceptually similar to buffers, its input and output are connected
    to distinct buses. The terminal reads the input bus' signal and writes 
    that same signal to the output bus. It's possible to use a Terminal as a NOT
    gate as well, in which case the output would be the logical negation of the input.
    The input and output for every circuit Block is a Terminal.
    Optionally, it is possible to toggle whether the output propagates the signal
    to the bus or not. If self.connected is tied to GND, then the signal will not propagate
    this is analogous to being at a High Impedance.
    """
    VDD = Bus(1, 1)
    GND = Bus()

    def __init__(self, in_bus=None, bus_len=0, enable=None, invert=False):
        self._in_bus = None
        self.out_bus = Bus()
        self.bus_len = bus_len
        self.invert = invert
        if in_bus:
            self.in_bus = in_bus
        if not enable:
            self.enable = self.VDD
        else:
            self.enable = enable

    @property
    def in_bus(self):
        return self._in_bus

    @in_bus.setter
    def in_bus(self, bus):
        if len(bus) != self.bus_len and self.bus_len != 0:
            raise ValueError("Bus size incompatible with requirements")
        self._in_bus = bus
        self.out_bus.extend(len(bus))
        
    def propagate(self):
        """Transmit the signal from the in_bus to the out bus if Bus is connected"""
        in_sig = self.in_bus.signal
        if self.enable == self.VDD:
            self.out_bus.signal = in_sig if not self.invert else in_sig.complement()
