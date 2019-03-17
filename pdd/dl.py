from collections import namedtuple
from core import Updater, Signal, Wire
import logging

logger = logging.getLogger(__name__)

u = Updater()
       
class Bus:
    """
    The Bus class is an abstraction for a wire or a group of wires. 
    Bus connects Terminals. Bus are made up of Wires and are sliceable.
    Slicing a Bus returns a new Bus with the matching wires. Any changes made
    to the original Bus propagates to the sliced Bus.
    Bus value is given by Signal which gives a higher level API. Two Bus are equal if
    their signals are equal
    """
    BusEvent = namedtuple('BusEvent', ('bus'))
    updater = u
    auto_update = False

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
        self.updater.notify(event)
        if self.auto_update and not self.updater.updating:
            self.updater.update()
            
    @classmethod
    def _from_wires(cls, wires):
        """Init bus from a sequence of wires"""
        bus = Bus(len(wires))
        bus.wires = wires
        return bus
 
    
class Terminal:
    """
    Terminals are boundaries between the outside world and a circuit.

    Terminals are conceptually similar to buffers, it has an input Bus 'a' and 
    an output Bus 'y', upon that configuartion it will simply propagate the signal of 'a' to 'y'.

    The concept of "bubbles" as is defined in digital circuits is implemented,
    if bubble == True the output signal is negated, that is, 'y' = NOT 'a'.
    
    The input and output for every circuit Block is a Terminal.

    Finally, it is possible to simulate tri-state logic at the terminals (ie whether 
    the signal at 'a' gets propagated to 'y'). If self.en is tied to GND 
    (or any length 1 Bus with signal 0), then the signal will not propagate this 
    is analogous to being at a High Impedance. A length 1 Bus with signal 1
    causes the signal to propagate.
    
    Terminal has a size which is a constrait of which Bus objects it accepts.
    Any Bus of len size can be used for that instance of Terminal. 
    Size is required for Terminal init, upon init valid Buses are created
    and assigned to 'a' and 'y'. Optionally, the 'a' and 'y' Buses can be
    given at init.
    """
    VDD = Bus(1, 1)
    GND = Bus(1, 0)

    def __init__(self, size, a=None, y=None, en=None, bubble=False):
        self.size = size
        self._a = None
        self._y = None
        self._en = None
        self.bubble = bubble
        self.a = a if a else Bus(size)
        self.y = y if y else Bus(size)
        self.en = en if en else self.VDD

    def setter(self, attr, value, size):
        """DRY for setter methods. attr is a string, value is a Bus object.
        Checks that value is of type Bus and sets the attr"""
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
        self.setter('en', value, 1) 

    def propagate(self):
        """Transmit the signal from the in_bus to the out bus if Bus is connected"""
        sig = self.a.signal
        if self.en == self.VDD:
            self.y.signal = sig if not self.bubble else sig.complement()

class BaseCircuit:
    """
    Accepted kwargs:
    size: size of the data carrying Bus in the circuit
    bubbles: Sequence with labels for terminals whose bubble should be set
    labels (eg 'a', 'y'): Bus that will be connected to the circuit's terminals
    
    Either a data carrying Bus or size must be part of kwargs otherwise an Exception is raised
    
    """
    updater = u
    def __init__(self, **kwargs):
        #self.input_labels = []
        #self.output_labels = []
        #self.sizes = {} change me
        try:
            if not type(self.sizes) is dict:
                #????????????????
                self.sizes = {}
        except AttributeError:
            self.sizes = {}
        
        #Logic that ensures size of circuit is defined. Makes the whole thing easier
        self.labels = self.input_labels + self.output_labels
        if 'size' in kwargs:
            size = kwargs['size']
        else:
            buses = [kwargs[label] for label in self.labels if label not in self.sizes and label in kwargs]
            try:
                size = len(buses[0])
            except IndexError:
                #maybe set size to 1 instead of raising an error?
                raise Exception("Need a bus or size!")
        d = {label : size for label in self.labels if label not in self.sizes}
        self.sizes.update(d)
        self.terminals = {label : Terminal(size) for label, size in self.sizes.items()}

        if 'bubbles' in kwargs:
            self.set_bubbles(**{label : True for label in kwargs['bubbles']})

        self.connect(**kwargs)
        self.make()

    def output(self, label=''):
        """Return Bus output bus attached to terminal `label`. If no label is given
        return the Bus of first output"""
        if not label:
            label = self.output_labels[0]
        return self.terminals[label].y

    def outputs(self, *args):
        """Return list with output Buses attached to terminals in args"""
        #add logic for invalid label
        return [self.terminals[label].y for label in args]

    def connect(self, **kwargs):
        for label, bus in kwargs.items():
            if label in self.input_labels:
                self.terminals[label].a = bus
            elif label in self.output_labels:
                self.terminals[label].y = bus
        self.update_triggers()
        self.update_attributes()

    def update_triggers(self):
        """Update the trigger Buses in the observer object"""
        self.updater.unsubscribe(self, self.get_inputs())
        self.updater.subscribe(self, self.get_inputs())
        

    def make(self):
        """Make must be implemented by subclasses. The body of make contain the
        the creation of circuit blocks used by the class, the association between
        these circuits and the wiring (ie connecting Bus to inputs/outputs)"""
        pass

    def get_inputs(self):
        """Return an Input object. Input objects have named attributes for each input
        in self. The value of the attribute is the same as self.terminals[label].y
        Used as syntathic sugar which eases the job of writing make()."""
        buses = {label: self.terminals[label].y for label in self.input_labels}
        return self.namedtuple_factory('Inputs', buses)

    def set_outputs(self, **kwargs):
        """Used to set the outputs of a circuit in make(). 
        kwargs keys are labels and kwargs values are buses.
        eg self.terminals['y'].a = kwargs['y']"""
        #add logic to handle case where bus doesn't exist
        for label, bus in kwargs.items():
            if label in self.output_labels:
                self.terminals[label].a = bus 

    def set_bubbles(self, **kwargs):
        """Set bubbles in terminals present in kwargs.
        kwarg keys are labels and values is a bool"""
        #add logic to handle case where bus doesn't exist
        for key, value in kwargs.items():
            self.terminals[key].bubble = value

    def update(self):
        """Mimic the behavior of a digital circuit. Each time the voltage
        of a wire in a digital circuit changes the circuit output changes.
        update should - under normal circumstances be called by the Updater
        object automatically"""
        for label in self.input_labels:
            self.terminals[label].propagate()

    @staticmethod
    def namedtuple_factory(name, dict):
        """Factory method for namedtuples. Create a nametuple factory and
        return an instance of the factory initialized to the values in dict"""
        factory = namedtuple(name, list(dict.keys()))
        return factory(**dict)

    def update_attributes(self):
        for label in self.input_labels:
            setattr(self, label, self.terminals[label].a)
        for label in self.output_labels:
            setattr(self, label, self.terminals[label].y)
