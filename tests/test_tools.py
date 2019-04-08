import unittest, logging
import truth_tables
from tools import TruthTable, IOHelper, SignalGen
from dl import Bus

class TestTruthTable(unittest.TestCase):

    def test_table_eq(self):
        t1 = truth_tables.AND
        t2 = truth_tables.OR
        self.assertEqual(t1, t1)
        self.assertNotEqual(t1, t2)


class TestIOHelper(unittest.TestCase):

    def test_signals(self):
        signals = IOHelper.parse_signals('aux/signals.txt')
        expected = [dict(a=3, b=5, c=0), dict(a=4), dict(a=2, b=1, c=0)]
        self.assertEqual(signals, expected)

    def test_memory(self):
        words = IOHelper.parse_memory('aux/memory.txt')
        expected = [3, 2, 13]
        self.assertEqual(words, expected)
        
class TestSignalGen(unittest.TestCase):

    def setUp(self):
        self.signals = [dict(a=1, b=2), dict(a=2, b=3), dict(b=4)]
        
    def test_next(self):
        bus_a = Bus(4)
        bus_b = Bus(4)
        gen = SignalGen(dict(a=bus_a, b=bus_b), self.signals)
        self.assertEqual(int(bus_a.signal), 0)
        self.assertEqual(int(bus_b.signal), 0)
        gen.next()
        self.assertEqual(int(bus_a.signal), 1)
        self.assertEqual(int(bus_b.signal), 2)
        gen.next()
        self.assertEqual(int(bus_a.signal), 2)
        self.assertEqual(int(bus_b.signal), 3)
        gen.next()
        self.assertEqual(int(bus_b.signal), 4)

    def test_sweep(self):
        #use truthtable obj to test this
        bus_a = Bus()
        bus_b = Bus()
        d = dict(a=bus_a, b=bus_b)
        gen = SignalGen.sweep(d)

    def test_sweep_multibit(self):
        #same as above
        ba = Bus(2)
        bb = Bus(2)
        d = dict(a=ba, b=bb)
        gen = SignalGen.sweep(d)
        
        
    
if __name__ == '__main__':
    logging.basicConfig(filename='{}.log'.format(__file__), filemode='w', level=logging.DEBUG)
    unittest.main()
