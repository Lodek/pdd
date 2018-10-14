import unittest
from core import Signal, Bus, Terminal

class TestSignal(unittest.TestCase):

    def test_operations(self):
        a = Signal('100')
        b = Signal('011')
        self.assertTrue(Signal('000') == Signal.AND(a,b))
        self.assertTrue(Signal('111') == Signal.OR(a,b))
        self.assertTrue(Signal('111') == Signal.XOR(a,b))
        self.assertTrue(Signal('011') == Signal.NOT(a))

        
if __name__ == '__main__':
    unittest.main()
