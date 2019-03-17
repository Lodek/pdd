import unittest, logging
from dl import Bus
from blocks import Gate
from core import Signal
   

class TestGate(unittest.TestCase):

    def sweep_signals(self, buses):
        """buses[0] will be the MSB and bus[-1] LSB"""
        bus = buses.pop(0)
        while buses:
            bus = bus + buses.pop(0)
        for i in range(len(bus) ** 2):
            bus.signal = i
            yield i
 
    def base_tester(self, circuit, output_bus, expected_signals):
        """DRY for testing circuit blocks from a truth table"""
        inputs = [circuit.terminals[label].a for label in circuit.input_labels]
        outputs = []
        for _ in self.sweep_signals(inputs):
           circuit.update()
           outputs.append(output_bus.signal)
        for expected, generated in zip(expected_signals, outputs):
            self.assertEqual(expected, generated)

    def test_AND(self):
        """Test AND gate"""
        g = Gate(Gate.AND, size=1)
        expected = [Signal(i, 1) for i in [0,0,0,1]]
        self.base_tester(g, g.y, expected)

    def test_OR(self):
        """Test OR gate"""
        g = Gate(Gate.OR, size=1)
        expected = [Signal(i, 1) for i in [0,1,1,1]]
        self.base_tester(g, g.y, expected)

    def test_XOR(self):
        """Test XOR gate"""
        g = Gate(Gate.XOR, size=1)
        expected = [Signal(i, 1) for i in [0,1,1,0]]
        self.base_tester(g, g.y, expected)



if __name__ == '__main__':
    logging.basicConfig(filename='core.log', filemode='w', level=logging.DEBUG)
    unittest.main()
