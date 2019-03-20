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

    def test_add(self):
        a = Bus(1, 1)
        b = Bus(1, 0)
        c = a + b
        self.assertEqual(c.signal.value, 2)

    def test_branch(self):
        a = Bus(1)
        branched_a = a.branch(4)
        self.assertEqual(len(branched_a), 4)
        self.assertEqual(branched_a.signal, Signal(0, 4))
        a.signal = 1
        self.assertEqual(branched_a.signal, Signal(2**4-1, 4))

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
