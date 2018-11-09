import unittest
from core import Signal, Bus, Terminal, VDD, GND

class TestSignal(unittest.TestCase):

    def test_operations(self):
        a = Signal('100')
        b = Signal('011')
        c = Signal('100')
        self.assertEqual(Signal('000'), Signal.AND(a,b))
        self.assertEqual(Signal('111'), Signal.OR(a,b))
        self.assertEqual(Signal('111'), Signal.XOR(a,b))
        self.assertEqual(Signal('011'), Signal.NOT(a))
        self.assertEqual(a, c)
        

class TestBus(unittest.TestCase):

    def test_bus(self):
        init_len = 4
        b = Bus(init_len)
        b.signal = '1010'
        self.assertEqual(b.signal, Signal('1010'))
        self.assertEqual(len(b), init_len)
        with self.assertRaises(ValueError):
            b.signal = '10101'
        new_len = 8
        b.extend(new_len)
        new_sig = '11001100'
        b.signal = new_sig
        self.assertEqual(len(b), new_len)
        self.assertEqual(b.signal, Signal(new_sig))


    def test_slice(self):
        b = Bus(4)
        b.signal = '1010'
        b1 = b[1]
        b2 = b[2:]
        self.assertEqual(Signal('0'), b1.signal)
        self.assertEqual(Signal('10'), b2.signal)
        b.signal = '0101'
        self.assertEqual(Signal('1'), b1.signal)
        self.assertEqual(Signal('01'), b2.signal)
        

class TestTerminal(unittest.TestCase):

    def setUp(self):
        self.term = Terminal()
        bus = Bus(4)
        bus.signal = '1010'
        self.term.in_bus = bus
        
    def test_terminal(self):
        """Tests basic Terminal functionality"""
        self.term.propagate()
        self.assertEqual(self.term.in_bus.signal, self.term.out_bus.signal)

    def test_invert(self):
        self.term.invert = True
        self.term.propagate()
        self.assertEqual(self.term.in_bus.signal.complement(), self.term.out_bus.signal)

    def test_connected(self):
        self.term.connected = GND
        self.term.propagate()
        self.assertNotEqual(self.term.in_bus.signal, self.term.out_bus.signal)

    def test_bus_len(self):
        term = Terminal(bus_len=2)
        bus = Bus()
        with self.assertRaises(ValueError):
            term.in_bus = bus
        
if __name__ == '__main__':
    unittest.main()
