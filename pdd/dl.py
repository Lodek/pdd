from collections import namedtuple
from pdd.core import Updater, Signal, Wire, StaticWire
import warnings, logging

logger = logging.getLogger(__name__)
u = Updater()
Wire.updater = u
       
class Bus:
    """
    The Bus class is an abstraction for a wire or a group of wire objects 
    which are analogous to ideal wires in digital circuits. 
    Bus connects Terminals together thus conecting circuits.

    The class provides operations to ease the handling of the wires in a
    bus such as: slicing, branching a wire into many, combining a sequence
    of buses into a single bus.

    Operating on a Bus object return a new Bus with made up by the 
    specified wires. Any changes made to the those wires will manifest
    to all buses that contain those wires.

    Bus are data carries and that data is specified by the bit value of
    the wires. To provide a higher level usage Bus uses signal objects 
    instead to handle that.
    Two buses are equal if their signal are equal, len(bus) return the
    number of wires.
    """
    _vdd_wire = StaticWire(1)
    _gnd_wire = StaticWire(0)
    def __init__(self, n=1, signal=0):
        if n <= 0:
            raise ValueError('Bus size must be > 0')
        self.wires = [Wire() for _ in range(n)]
        self.signal = signal
        logger.debug(repr(self))

    def __repr__(self):
        s = '{}: signal={}; len={};'
        return s.format(self.__class__, str(self.signal), len(self))
        
    def __len__(self):
        return len(self.wires)

    def __getitem__(self, index):
        """Creates a new Bus from the sliced wires, returns new Bus"""
        wires = self.wires[index]
        if type(wires) != list:
            wires = [wires]
        return Bus._from_wires(wires)

    def __eq__(self, other):
        #I feel like I shouldn't do that. Buses can't be "equal"
        return True if self.signal == other.signal else False

    @property
    def signal(self):
        """Returns Signal object for bus"""
        return Signal.from_wires(self.wires)
        
    @signal.setter
    def signal(self, value):
        """Assigns a new Signal to the bus and notifies the updater"""
        new_signal = value if type(value) is Signal else Signal(value, len(self))
        if self.signal == new_signal:
            return
        else:
            for wire, bit in zip(self.wires, new_signal.bits):
                wire.bit = bit

   
    def __add__(self, other):
        """Add Bus objects by combining wires. If operation is A + B,
        the result is a Bus where A is the MSB and B is LSB, that is
        the lefthand bits get shifted to the left.
        This operation is not commutative."""
        try:
            wires = other.wires + self.wires 
            return self._from_wires(wires)
        except AttributeError:
            return NotImplemented

    @classmethod
    def merge(self, buses):
        """Return a unified Bus from a list of buses. buses[0] will
        represent the LSB of the resulting bus"""
        buses = list(buses) #makes copy of buses
        bus = buses.pop()
        while buses:
            bus = bus + buses.pop()
        return bus

    def sweep(self):
        """Generator that sweeps over all possible signs for Bus.
        Start at 0 and end at the last value combination.
        Essentially counts from 0 to 2 ^ len(self)"""
        for i in range(2 ** len(self)):
            yield i

    @staticmethod
    def _get_op_len(l):
        """DRY for methods that modify a bus to a length, return len of new Bus.
        l can be an integer value or a Bus.
        If l is a bus then len(l) > len(self) must be true and
        if l is an int l > len(self) otherwise raise ValueError"""
        if type(l) is Bus:
            n = len(l)
        else: n = l
        return n
 
    def branch(self, l):
        """Branche a Bus into a Bus of length n. Analogous to making a Bus
        out of the same wire. Always branch the 0th wire"""
        n = self._get_op_len(l)
        wire = self.wires[0]
        wires = [wire] * n
        return self._from_wires(wires)

    def set(self):
        """Sets all wires in Bus to 1"""
        for wire in self.wires:
            wire.bit = 1

    def reset(self):
        """Set all wires in Bus to 0"""
        for wire in self.wires:
            wire.bit = 0

    def pulse(self):
        """Consecutive call to set and reset"""
        self.set()
        self.reset()

    def split(self):
        """Return self as a list of 1 bit buses"""
        buses = [self._from_wires([wire]) for wire in self.wires]
        return buses

    def sign_extend(self, l):
        """Return a sign extended version of self of length l by padding bus
        with the MSB"""
        n = self._get_op_len(l)
        diff = n - len(self)
        wires = self.wires + [self.wires[-1]] * diff
        return self._from_wires(wires)
        
    def extend(self, value, l):
        """Return an extended version of self with added padding
        Padding will be either 0 or 1 given by value. l determines the len
        of the new Bus"""
        n = self._get_op_len(l)
        diff = n - len(self)
        if value == 0:
            padding = [self._gnd_wire] * diff
        if value == 1:
            padding = [self._vdd_wire] * diff
        wires = self.wires + padding
        return self._from_wires(wires)

    def zero_extend(self, l):
        """Zero extend self to length l"""
        return self.extend(0, l)

    def vdd_extend(self, l):
        """vdd extend self to length l"""
        return self.extend(1, l)
    
       
    @classmethod
    def _from_wires(cls, wires):
        """Initialize Bus from a sequence of wires"""
        bus = cls(len(wires))
        bus.wires = wires
        return bus
 
    @classmethod
    def vdd(cls, l=1):
        """Return VDD, a StaticWire, meaning that it is always 1. Optionally
        receive l, integer or Bus, which determines the length of the Bus."""
        n = cls._get_op_len(l)
        wires = [cls._vdd_wire] * n
        return cls._from_wires(wires)

    @classmethod
    def gnd(cls, l=1):
        """Return GND, a StaticWire, meaning that it is always 0. Optionally
        receive l, integer or Bus, which determines the length of the Bus."""
        n = cls._get_op_len(l)
        wires = [cls._gnd_wire] * n
        return cls._from_wires(wires)
        
    
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
    vdd = Bus.vdd()
    def __init__(self, size, label, a=None, y=None, en=None, bubble=False):
        self.size = size
        self.label = label
        self._a = None
        self._y = None
        self._en = None
        self.bubble = bubble
        self.a = a if a else Bus(size)
        self.y = y if y else Bus(size)
        self.en = en if en else self.vdd

    def __repr__(self):
        s = '{}: label={}; a={}; y={}; en={}; bubble={};'
        return s.format(self.__class__, self.label, self.a, self.y, self.en, self.bubble)
        
    def _setter(self, attr, value, size):
        """DRY for setter methods. attr is a string, value is a Bus object.
        Checks that value is of type Bus and sets the attr"""
        logger.info(f'Setting {self} {attr} connection with {value}')
        if type(value) is not Bus:
            e = TypeError('Terminal attributes must be Buses')
            logger.exception(repr(self))
            raise e
        elif len(value) != size:
            e = ValueError('Bus size incompatible with Terminal')
            logger.exception(repr(self))
            raise e
        else:
            self.__dict__['_'+attr] = value

    def _getter(self, attr):
        """DRY for getter method"""
        return self.__dict__['_'+attr]

    a = property(lambda self: self._getter('a'), lambda self, x : self._setter('a', x, self.size))
    y = property(lambda self : self._getter('y'), lambda self, x : self._setter('y', x, self.size))
    en = property(lambda self: self._getter('en'), lambda self, x : self._setter('en', x, 1))

    def propagate(self):
        """Transmit the signal from the in_bus to the out bus if Bus is connected"""
        logger.debug(f'Propagate {repr(self)}')
        sig = self.a.signal
        if self.en.signal == self.vdd.signal:
            self.y.signal = sig if not self.bubble else sig.complement()

    def get_triggers(self):
        return self.a.wires + self.en.wires

class BaseCircuit:
    """
    Accepted kwargs:
    size: size of the data carrying Bus in the circuit
    bubbles: Sequence with labels for terminals whose bubble should be set
    labels (eg 'a', 'y'): Bus that will be connected to the circuit's terminals
    
    Either a data carrying Bus or size must be part of kwargs otherwise an Exception is raised
    """
    updater = u
    parent = None
    children = []
    def __init__(self, **kwargs):
        #self.input_labels = []
        #self.output_labels = []
        self.triggers = []
        self.parent = None
        self.children = []
        try:
            self.sizes = dict(self.sizes)
        except AttributeError:
            self.sizes = {}
        
        #Logic that ensures size of circuit is defined. Makes the whole thing easier
        labels = self.input_labels + self.output_labels
        if 'size' in kwargs:
            size = kwargs['size']
        else:
            buses = [kwargs[label] for label in labels if label not in self.sizes and label in kwargs]
            try:
                size = len(buses[0])
            except IndexError:
                size = 1
                warnings.warn('No circuit data size given. Setting it to 1')
        d = {label : size for label in labels if label not in self.sizes}
        self.sizes.update(d)
        self.terminals = {label : Terminal(size, label) for label, size in self.sizes.items()}

        if 'bubbles' in kwargs:
            self.set_bubbles(**{label : True for label in kwargs['bubbles']})
        if 'tristate' in kwargs:
            self.set_tristate(**kwargs['tristate'])


        self.connect(**kwargs)

        self.parent = self.get_parent()
        logger.debug('Parent of circuit {} set to {}'.format(self, self.parent))
        self.parent.children.append(self)
        self.make_setup()
        self.make()
        self.make_tear_down()

        self.update_triggers()

    def __repr__(self):
        s = '{}: '.format(self.__class__.__name__)
        return s + str(self.state)

    @staticmethod
    def get_parent():
        """Return value of parent set in BaseCircuit class"""
        return BaseCircuit.parent

    @staticmethod
    def set_parent(value):
        """Set BaseCircuit parent attribute to value"""
        BaseCircuit.parent = value

    def make_setup(self):
        """Setup for make. Sets self as the parent in BaseCircuit"""
        logger.debug('Make setup for circ. {}'.format(self))
        self.set_parent(self)

    def make_tear_down(self):
        """Set BaseCircuit parent attribute to self"""
        logger.debug('Make teardown for circ. {}'.format(self))
        self.set_parent(self.parent)
        
    def connect(self, **kwargs):
        logger.debug(f'connecting {self}')
        for label, bus in kwargs.items():
            if label in self.input_labels:
                self.terminals[label].a = bus
            elif label in self.output_labels:
                self.terminals[label].y = bus
        if kwargs:
            pass
            #kwargs not empty, imaginary labels
        self.update_triggers()
        self.update()

    def connect_sequence(self, seq):
        """Receive a sequence of buses and sequentially
        assign bus to input terminals. The order of the assignment
        is given by self.input_labels. len(seq) must be equal to
        len(input_labels)"""
        if len(self.input_labels) != len(seq):
            raise ValueError('Not enough buses for all inputs')
        connections = {label : bus for label, bus in zip(self.input_labels, seq)}
        self.connect(**connections)

    def update_triggers(self):
        """Update the trigger Buses in the observer object"""
        self.updater.unsubscribe(self, self.triggers)
        nested_wires = [terminal.get_triggers() for terminal in self.terminals.values()]
        self.triggers = [wire for wires in nested_wires for wire in wires]
        self.updater.subscribe(self, self.triggers)
        
    def make(self):
        """Make must be implemented by subclasses. The body of make contain the
        the creation of circuit blocks used by the class, the association between
        these circuits and the wiring (ie connecting Bus to inputs/outputs)"""
        pass

    def get_inputs(self):
        #rename this to get_input_nodes or something
        """Return an Input object. Input objects have named attributes for each input
        in self. The value of the attribute is the same as self.terminals[label].y
        Used as syntathic sugar which eases the job of writing make()."""
        buses = {label: self.terminals[label].y for label in self.input_labels}
        buses.update({label: self.terminals[label].a for label in self.output_labels})
        return self.namedtuple_factory('Nodes', buses)

    def set_outputs(self, **kwargs):
        """Used to set the outputs of a circuit in make(). 
        kwargs keys are labels and kwargs values are buses.
        eg self.terminals['y'].a = kwargs['y']"""
        #add logic to handle case where bus doesn't exist
        for label, bus in kwargs.items():
            if label in self.output_labels:
                self.terminals[label].a = bus 
        self.update_triggers()

    def get_bubbles(self):
        return {label : self.terminals[label].bubble for label in self.input_labels + self.output_labels}

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
        for terminal in self.terminals.values():
            terminal.propagate()

    @staticmethod
    def namedtuple_factory(name, dict):
        """Factory method for namedtuples. Create a nametuple factory and
        return an instance of the factory initialized to the values in dict"""
        factory = namedtuple(name, list(dict.keys()))
        return factory(**dict)

    def __setattr__(self, attr, value):
        if attr == 'input_labels':
            object.__setattr__(self, attr, value)
        elif attr in self.input_labels:
            self.terminals[attr].a.signal = value
        else:
            object.__setattr__(self, attr, value)
        
    def __getattr__(self, attr):
        if attr == 'input_labels' or attr == 'output_labels':
            object.__getattribute__(self, attr)
        elif attr in self.input_labels:
            return self.terminals[attr].a
        elif attr in self.output_labels:
            return self.terminals[attr].y
        else:
            object.__getattribute__(self, attr)

    def get_bus(self, label):
        """Return the Bus matching label"""
        if label in self.output_labels:
            return self.terminals[label].y
        elif label in self.input_labels:
            return self.terminals[label].a
        else:
            raise ValueError('Label "{}" not in circuit'.format(label))

    def get_buses(self, buses):
        """Expect buses to be a sequence of strings corresponding to labels.
        returns a list with all the buses matching the labels"""
        return [self.get_bus(label) for label in buses]

    def set_tristate(self, **kwargs):
        for label, bus in kwargs.items():
            self.terminals[label].en = bus

    @property
    def state(self):
        i = {label : str(self.terminals[label].a.signal) for label in self.input_labels}
        o = {label : str(self.terminals[label].y.signal) for label in self.output_labels}
        i.update(o)
        return i

    @property
    def state_int(self):
        i = {label : int(self.terminals[label].a.signal) for label in self.input_labels}
        o = {label : int(self.terminals[label].y.signal) for label in self.output_labels}
        i.update(o)
        return i

    @property
    def auto_update(self):
        return Wire.auto_update

    @auto_update.setter
    def auto_update(self, value):
        if not type(value) is bool:
            raise ValueError('Value must be bool')
        Wire.auto_update = value

BaseCircuit.parent = BaseCircuit

