from gate import Gate
from core import Bus
class TestGate(unittest.TestCase):

    def setUp(self):
        self.a = Bus('101')
        self.b = Bus('001')
        
    def test_and(self):
        g = Gate((self.a, self.b), 'and')
        
