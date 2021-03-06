"""Module containg abstractions which are used to implement digital logic. The objects in this module aren't physical entities as much as concepts in digital logic"""

from collections import defaultdict, namedtuple, deque
import logging

logger = logging.getLogger(__name__)

class Wire:
    """
    Wire represents a bit of data. Changes to Wire create Events which
    are notified to updater.

    Wires are immutable therefore they are the correct candidates for event
    generation.
    
    Wire must be assigned an instance of Updater before use.
    If auto_update is True, Wire will call updater.update() every time
    a set is made
    """
    Event = namedtuple('Event', ('obj'))
    updater = None
    auto_update = True
    def __init__(self, bit=0):
        self._bit = 0
        self.bit = bit

    def __repr__(self):
        s = '{}: bit={}; id={}'
        return s.format(self.__class__, self.bit, id(self))

    @property
    def bit(self):
        return self._bit
    
    def __repr__(self):
        s = '{}: bit={}; id={}'
        return s.format(self.__class__, self.bit, id(self))


    @bit.setter
    def bit(self, value):
        if self._bit == value:
            return
        self._bit = value
        event = self.Event(self)
        self.updater.notify(event)
        if not self.updater.updating and self.auto_update:
            self.updater.update()
        
class StaticWire:
    """
    Like wire but does not support assignment.
    Used exclusively for Bus.vdd and Bus.gnd.
    """
    def __init__(self, bit):
        self._bit = bit

    @property
    def bit(self):
        return self._bit
    
    @bit.setter
    def bit(self, value):
        e = TypeError('StaticWire does not support assignment')
        logger.exception(e)
        raise e

class Signal:
    """
    Signal abstracts digital signals and is used to set values on a Bus.
    Signal provides an API to deal with digital signals. The data carried by
    a Bus is encoded as a Signal. Signal provides methods to perform logical operations
    that take Signal objects as operands and return a new instace of Signal.
    """
    def __init__(self, value, size):
        if type(value) is int:
            self.value = value
        else:
            msg = 'Argument of type {} to {}. Must be an Integer'
            e = TypeError(msg.format(type(value), self.__class__))
            logger.exception(e)
            raise e
        self._size = size
        logger.debug(repr(self))

    @classmethod
    def from_wires(cls, wires):
        """Initialize a signal object from a list of wires"""
        sig = 0
        for i, wire in enumerate(wires):
            sig |= wire.bit << i
        return cls(sig, len(wires))
        
    @property
    def bits(self):
        """Convert value into a sequence of 0s and 1s, essentially
        a list with its binary representation.
        The 0th element of the sequence represents the 0th bit."""
        return tuple(self.value >> i & 0x1 for i in range(self._size))

    def __eq__(self, other):
        return self.value == other.value

    def __repr__(self):
        s = '{}: value={};'
        return s.format(self.__class__, hex(self.value))
        
    def __int__(self):
        return self.value
    
    def __str__(self):
        return hex(self.value)

    def complement(self):
        return Signal.NOT(self)
    
    @classmethod
    def NOT(cls, a):
        mask = 0
        for i in range(a._size):
            mask |= 1 << i
        value = ~a.value & mask
        return cls(value, a._size)

    @classmethod
    def OR(cls, a, b):
        value = a.value | b.value
        return cls(value, a._size)

    @classmethod
    def AND(cls, a, b):
        value = a.value & b.value
        return cls(value, a._size)

    @classmethod
    def XOR(cls, a, b):
        value = a.value ^ b.value
        return cls(value, a._size)

class Updater:
    """
    Implementation of the Observer design pattern.

    Signal carriers in PDD are Wires. Any Wire that suffers a change will notify
    Updater of the event. A BaseCircuit is depedent on a group of Wires, meaning
    that any change made to those wires will change the circuit. Circuits then 
    subscribe to Updater to be updated upon Wire changes.

    Handling events, presumably, begins a cascate of events by making changes
    to others Wires which notifies of further events. Updater's job for the cycle
    is done when no new events are generated by an update call.

    There is a maximum threshold (default 2**10, change within init) to Updater's number 
    of calls per cycle in order to avoid deadlocks caused by improper circuits
    (e.g. unstable circuits or circuits with cyclic paths)
    """
    def __init__(self, threshold=2**16):
        logger.info('Updater object created')
        self.auto_update = True
        self.threshold = threshold
        self.updating = False
        self.events = []
        self.relations = defaultdict(list)


    def subscribe(self, circuit, wires):
        """The subscribed circuit will be updater when an event is sourced by 
any wire in wires"""
        logger.debug('Subscribed {} to {}'.format(circuit, len(wires)))
        for wire in wires:
            self.relations[id(wire)].append(circuit)

    def unsubscribe(self, circuit, wires):
        """Circuit will no longer be updated upon change made to wire in wires"""
        for wire in wires:
            logger.debug('Unsubscribed {} from {}'.format(circuit, len(wires)))
            try:
                self.relations[id(wire)].remove(circuit)
            except ValueError:
                pass

    def notify(self, event):
        """Notifies Updater of new event, adds it to list of events"""
        logger.debug('New Updater event: ' + repr(event))
        self.events.append(event)
        
    def update(self):
        """Handle all events from this cycle until list is empty or threshold blows up.

        Handle all events in self.events. Events are handled in a FIFO manner
        and handling events is likely to cause more events to be generated.

        If the number of events in the cycle exceed threshold, raises a Runtime error
        with the last circuits handled.
        """
        #should change to a Breadth first algorithm
        logger.info('Handling events')
        self.updating = True
        deque_len = 50
        last = deque([None]*deque_len, maxlen=deque_len)
        for i in range(self.threshold):
            try:
                event = self.events.pop(0)
            except IndexError:
                self.updating = False
                break
            logger.debug('Handling event {}'.format(event))
            for circuit in self.relations[id(event.obj)]:
                last.append(circuit)
                logger.debug('updating circuit {}'.format(circuit))
                circuit.update()
        else:
            self.updating = False
            error_str = 'Update threshold blew up; check for cyclic path.'
            error = RuntimeError(error_str, last)
            raise error
