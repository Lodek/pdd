import unittest, logging
from collections import namedtuple
from core import Signal, Updater

class TestSignal(unittest.TestCase):

    def setUp(self):
        self.a = Signal(5, 3)
        self.b = Signal(0b11, 3)
        self.c = Signal(0x3, 3)
        return (self.a, self.b, self.c)
        
    def test_basic(self):
        a = Signal(0b101, 3)
        self.assertEqual(len(self.a), 3)
        self.assertEqual(self.a.to_bits(), (1,0,1))
        b = a.complement()
        c = Signal(0b010, 3)
        self.assertEqual(b, c)
        
    def test_consistency(self):
        bits_to_int = lambda signal : int(''.join([str(bit) for bit in signal.to_bits()]), 2)
        signals = self.setUp()
        for signal in signals:
            self.assertEqual(signal.data, bits_to_int(signal))

    def test_operations(self):
        a = Signal(0b0101, 4)
        b = Signal(0b1010, 4)
        self.assertEqual(Signal.OR(a, b), Signal(0b1111, 4))
        self.assertEqual(Signal.AND(a, b), Signal(0b0000, 4))
        self.assertEqual(Signal.XOR(a, b), Signal(0b1111, 4))
        

class mockCircuit:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def update(self):
        self.c.setter(self.a.data + self.b.data)
    
class mockBus:

    Event = namedtuple('Event', ('bus'))
    updater = None
    
    def __init__(self, data):
        self.data = data
        
    def setter(self, data):
        self.data = data
        self.updater.notify(self.Event(self))

class testUpdate(unittest.TestCase):

    def setUp(self):
        updater = Updater()
        mockBus.updater = updater
        ba = mockBus(3)
        bb = mockBus(5)
        bc = mockBus(0)
        circ_a = mockCircuit(ba, bb, bc)
        updater.subscribe(circ_a, (ba, bb))
        self.ba = ba
        self.bb = bb
        self.bc = bc
        self.updater = updater

    def test_updater(self):
        self.ba.setter(10)
        self.assertEqual(len(self.updater.events), 1)
        self.updater.handle_events()
        self.assertEqual(self.bc.data, 15)
        
if __name__ == '__main__':
    logging.basicConfig(filename='core.log', filemode='w', level=logging.DEBUG)
    unittest.main()
