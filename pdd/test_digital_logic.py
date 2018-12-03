import unittest, logging
from digital_logic import Wire, Bus
from core import Signal

class TestBus(unittest.TestCase):

    def test_basic(self):
        #10 = 0b1010
        b = Bus(4)
        self.assertEqual(len(b), 4)
        b.signal = 10
        self.assertEqual(b.signal, Signal(10, 4))
        bb = b[3]
        self.assertEqual(bb.signal, Signal(1, 1))
        bb.signal = 0
        self.assertEqual(b.signal, Signal(2, 4))
        
        

if __name__ == '__main__':
    logging.basicConfig(filename='pdd.log', filemode='w', level=logging.DEBUG)
    unittest.main()
