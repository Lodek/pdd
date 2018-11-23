from core import Bus, Gate
import unittest

class TestGate(unittest.TestCase):

    def setUp(self):
        self.a = Bus.from_signal('101')
        self.b = Bus.from_signal('001')
        
    def test_and(self):
        c = {'a':self.a, 'b':self.b}
        g = Gate('xor', c)
        g.update()
        print(g.output().signal)
        self.a.signal = '110'
        self.b.signal = '100'
        
if __name__ == '__main__':
    unittest.main()
        
