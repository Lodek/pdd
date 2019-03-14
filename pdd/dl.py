from collections import namedtuple
from core import Updater, Signal, Wire
import logging

updater = Updater() #module wide declartion of Updater
logger = logging.getLogger(__name__)
       
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
        logger.debug(repr(self))

    def __repr__(self):
        s = '{}: signal={}; len={};'
        return s.format(self.__class__, self.signal, len(self))
        
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

    def __add__(self, other):
        """Combine buses self + other where the most siginifcant bits are 
        assigned to self. Notice that this operation is not commutative."""
        try:
            wires = other.wires + self.wires 
            return self._from_wires(wires)
        except AttributeError:
            return NotImplemented

    @property
    def signal(self):
        """Returns Signal object for bus"""
        return Signal(int(self), len(self))
        
    @signal.setter
    def signal(self, value):
        """Assigns a new Signal to the bus and notifies the updater"""
        #should I check for other types of value? What if user gives a string?
        #should I handle that here or at signal?
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
        """Init bus from a sequence of wires"""
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
    GND = Bus(1, 0)

    def __init__(self, size, a=None, y=None, en=None, bubble=False):
        self.size = size
        self._a = None
        self._y = None
        self._en = None
        self.bubble = bubble
        self.a = a
        self.y = y
        self.en = en if en else self.VDD

    def setter(self, attr, value, size):
        """DRY for setter methods. attr is a string, value is a Bus object.
        Checks that value is of type Bus and sets the attr"""
        if not value:
            return
        if type(value) is not Bus:
            raise TypeError
        elif len(value) != size:
            raise ValueError
        else:
            setattr(self, '_'+attr, value)

    @property
    def a(self):
        return self._a

    @a.setter
    def a(self, value):
        self.setter('a', value, self.size)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self.setter('y', value, self.size)

    @property
    def en(self):
        return self._en

    @en.setter
    def en(self, value):
        self.setter('en', value, self.size)

    def propagate(self):
        """Transmit the signal from the in_bus to the out bus if Bus is connected"""
        sig = self.a.signal
        if self.en == self.VDD:
            self.y.signal = sig if not self.bubble else sig.complement()
