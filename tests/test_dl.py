import unittest, logging, pdb
from dl import Bus, Terminal
from core import Signal

class TestBus(unittest.TestCase):

    def test_basic(self):
        b = Bus(4)
        self.assertEqual(len(b), 4)
        self.assertEqual(b.signal, Signal(0, 4))
        b.signal = 10
        self.assertEqual(b.signal, Signal(10, 4))

    def test_slicing(self):
        """Test Bus slicing feature. Test index and ranges"""
        b = Bus(4)
        b.signal = 0b1010
        bits = [0, 1, 0, 1]

        for subbus, bit in zip(b, bits):
            self.assertEqual(int(subbus.signal), bit)

        b_slice = b[2:]
        self.assertEqual(b_slice.signal, Signal(2, 2))
        b_slice.signal = 0b11
        self.assertEqual(b.signal, Signal(14, 4))

    def test_add_single_bit(self):
        """Add two buses of len 1"""
        a = Bus(1, 1)
        b = Bus(1, 0)
        c = a + b
        self.assertEqual(c.signal.value, 2)

    def test_add_multi_bit(self):
        """Add two buses of len != 1"""
        a = Bus(2, 1)
        b = Bus(2, 2)
        c = a + b
        self.assertEqual(c.signal.value, 6)

    def test_branch(self):
        """Test branching feature"""
        a = Bus(1)
        branched_a = a.branch(4)
        self.assertEqual(len(branched_a), 4)
        self.assertEqual(branched_a.signal, Signal(0, 4))
        a.signal = 1
        self.assertEqual(branched_a.signal, Signal(2**4-1, 4))

    def test_merge(self):
        a = Bus(1)
        b = Bus(1,1)
        buses = [a, b]
        merged = Bus.merge(buses)
        for a, b in zip(buses, merged):
            self.assertEqual(a, b)

    def test_set_reset(self):
        a = Bus(4)
        a.set()
        self.assertEqual(int(a.signal), 15)
        a.reset()
        self.assertEqual(int(a.signal), 0)

    def test_split(self):
        a = Bus(4, 0b0111)
        buses = a.split()
        for i, bus in enumerate(buses):
            self.assertEqual(a[i].signal, bus.signal)
            
    
class TestTerminal(unittest.TestCase):
    def setUp(self):
        self.t = Terminal(1)
        a = Bus(1, 1)
        y = Bus(1, 0)
        self.t.a = a
        self.t.y = y
 
    def test_basic(self):
        self.assertEqual(self.t.a.signal, Signal(1,1))
        self.assertEqual(self.t.y.signal, Signal(0,1))
        self.t.propagate()
        self.assertEqual(self.t.a, self.t.y)
       
    def test_bubble(self):
        self.t.propagate()
        self.t.bubble = True
        self.t.propagate()
        self.assertEqual(self.t.y.signal, Signal(0, 1))

    def test_propagate(self):
        self.t.en = Bus(1, 0)
        self.t.propagate()
        self.assertEqual(self.t.y.signal, Signal(0, 1))
        
    def test_setter(self):
        a = Bus(2, 1)
        with self.assertRaises(ValueError):
            self.t.a = a
        with self.assertRaises(ValueError):
            self.t.en = a
        with self.assertRaises(TypeError):
            self.t.a = 5
        

    
if __name__ == '__main__':
    logging.basicConfig(filename='digital_logic.log', filemode='w', level=logging.DEBUG)
    unittest.main()
