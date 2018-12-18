import unittest, logging
from digital_logic import Wire, Bus
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
                         
        
                         
        
        

if __name__ == '__main__':
    logging.basicConfig(filename='pdd.log', filemode='w', level=logging.DEBUG)
    unittest.main()
