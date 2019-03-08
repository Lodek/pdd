import unittest, logging, pdb
from digital_logic import Wire, Bus, Terminal
from core import Signal

class TestBus(unittest.TestCase):

    def rout(self):
        b = Bus(4)
    
    def test_basic(self):
        b = Bus(4)
        self.assertEqual(len(b), 4)
        self.assertEqual(b.signal, Signal(0, 4))
        b.signal = 10
        self.assertEqual(b.signal, Signal(10, 4))

    def test_slicing(self):
        b = Bus(4)
        b.signal = 0b1010
        b_slice = b[3]
        #2^3 bit
        self.assertEqual(b_slice.signal, Signal(1, 1))
        b_slice.signal = 0
        self.assertEqual(b.signal, Signal(0b0010, 4))
        b_slice = b[2:]
        self.assertEqual(b_slice.signal, Signal(0, 2))
        b_slice.signal = 0b11
        self.assertEqual(b.signal, Signal(14, 4))

    def test_extend(self):
        b = Bus(2, 0b11)
        b.extend(3)
        self.assertEqual(len(b), 3)
        self.assertEqual(b.signal, Signal(3, 3))
        b.signal = 0b100
        self.assertEqual(b.signal, Signal(4, 3))


class TestTerminal(unittest.TestCase):

    def setUp(self):
        self.in_bus = Bus(n=4, signal=2)
        self.term = Terminal()

    def test_init(self):
        self.term.in_bus = self.in_bus
        self.term.propagate()
        self.assertEqual(self.term.in_bus.signal, self.term.out_bus.signal)
        self.assertEqual(len(self.term.out_bus), 4)

    def test_invert(self):
        self.term.in_bus = self.in_bus
        self.term.invert = True
        self.term.propagate()
        self.assertEqual(self.term.in_bus.signal.complement(), self.term.out_bus.signal)

    def test_enable(self):
        self.term.in_bus = self.in_bus
        self.term.enable = self.term.GND
        self.term.propagate()
        self.assertEqual(Signal(0, 4), self.term.out_bus.signal)

    def test_bus_len_error(self):
        self.term.bus_len = 2
        with self.assertRaises(ValueError):
            self.term.in_bus = self.in_bus
        
        
    
if __name__ == '__main__':
    logging.basicConfig(filename='digital_logic.log', filemode='w', level=logging.DEBUG)
    unittest.main()
