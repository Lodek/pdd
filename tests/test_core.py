import unittest, logging
from collections import namedtuple
from core import Signal, Updater, Wire, StaticWire

class mockUpdater:
    events = []
    def notify(self, event):
        self.events.append(event)

class TestWire(unittest.TestCase):

    def setUp(self):
        Wire.updater = mockUpdater()
    
    def test_wire(self):
        w = Wire()
        self.assertEqual(w.bit, 0)
        w = Wire(1)
        self.assertEqual(w.bit, 1)

    def test_event(self):
        w = Wire()
        w.bit = 1
        self.assertTrue(w.updater.events != [])
        
class TestStaticWire(unittest.TestCase):

    def test_wire(self):
        w = StaticWire(0)
        self.assertEqual(w.bit, 0)
        w = StaticWire(1)
        self.assertEqual(w.bit, 1)
        with self.assertRaises(TypeError):
            w.bit = 0



class TestSignal(unittest.TestCase):

    def setUp(self):
        self.a = Signal(5, 3)
        self.b = Signal(0b11, 3)
        self.c = Signal(0x3, 3)
        return (self.a, self.b, self.c)
        
    def test_basic(self):
        a = Signal(0b101, 3)
        self.assertEqual(self.a.bits, (1,0,1))
        b = a.complement()
        c = Signal(0b010, 3)
        self.assertEqual(b, c)
        
    def test_consistency(self):
        bits_to_int = lambda signal : int(''.join(reversed([str(bit) for bit in signal.bits])), 2)
        signals = self.setUp()
        for signal in signals:
            self.assertEqual(signal.value, bits_to_int(signal))

    def test_operations(self):
        a = Signal(0b0101, 4)
        b = Signal(0b1010, 4)
        self.assertEqual(Signal.OR(a, b), Signal(0b1111, 4))
        self.assertEqual(Signal.AND(a, b), Signal(0b0000, 4))
        self.assertEqual(Signal.XOR(a, b), Signal(0b1111, 4))
        
class mockCircuit:
    updated = False
    def update(self):
        self.updated = True

class testUpdate(unittest.TestCase):
    def setUp(self):
        self.updater = Updater()
        Wire.updater = self.updater
        self.w1 = Wire()
        self.w2 = Wire()
        self.circ_a = mockCircuit()
        self.updater.events = [] #erases useless updates from init
        self.updater.subscribe(self.circ_a, (self.w1, self.w2))

    def test_subscribe(self):
        """Test Updater.subscribe method"""
        self.assertTrue(id(self.w1) in self.updater.relations)
        self.assertTrue(id(self.w2) in self.updater.relations)

    def test_unsubsribe(self):
        """Test Updater.unsubscribe method"""
        self.updater.unsubscribe(self.circ_a, (self.w1, self.w2))
        self.assertTrue(self.circ_a not in self.updater.relations.values())

    def test_update(self):
        self.assertFalse(self.updater.events)
        self.assertFalse(self.circ_a.updated)

        self.w1.bit = 1
        self.assertTrue(len(self.updater.events), 1)
        self.updater.update()
        self.assertTrue(self.circ_a.updated)


if __name__ == '__main__':
    logging.basicConfig(filename='core.log', filemode='w', level=logging.DEBUG)
    unittest.main()
