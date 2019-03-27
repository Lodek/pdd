import unittest, logging
from dl import Bus
from blocks import *
import truth_tables

class TestGate(unittest.TestCase):

    def tester(self, circuit, truth_table, input_order=[]):
        if not input_order:
            input_order = circuit.input_labels
        super_bus = Bus.bus_from_buses(circuit.get_buses(input_order))
        output_buses = {label: circuit.get_bus(label) for label in circuit.output_labels}
        generated_table = {label : [] for label in circuit.output_labels}
        for signal in super_bus.sweep():
            super_bus.signal = signal
            for label, bus in output_buses.items():
                generated_table[label].append(int(bus))
        for label in circuit.output_labels:
            self.assertEqual(truth_tabel[label], generated_table[label])
                
    def test_AND(self):
        """Test AND gate"""
        g = AND()
        self.tester(g, truth_tables.and)

    def test_OR(self):
        """Test OR gate"""
        g = OR()
        self.tester(g, truth_tables.or)

    def test_XOR(self):
        """Test XOR gate"""
        g = XOR()
        self.tester(g, truth_tables.xor)


if __name__ == '__main__':
    logging.basicConfig(filename='core.log', filemode='w', level=logging.DEBUG)
    unittest.main()
