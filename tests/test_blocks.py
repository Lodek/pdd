import unittest, logging
from dl import Bus
from blocks import *
import truth_tables
from tools import gen_output_table, TruthTable

class TestGate(unittest.TestCase):

    def _tester(self, circuit, truth_table):
        reference_table = TruthTable(circuit.input_labels, circuit.output_labels, 
                                     truth_table)
        generated_table = TruthTable(circuit.input_labels, circuit.output_labels, 
                                     gen_output_table(circuit))
        self.assertEqual(reference_table, generated_table)
                
    def test_AND(self):
        """Test AND gate"""
        g = AND()
        self._tester(g, truth_tables.AND)

    def test_OR(self):
        """Test OR gate"""
        g = OR()
        self._tester(g, truth_tables.OR)

    def test_XOR(self):
        """Test XOR gate"""
        g = XOR()
        self._tester(g, truth_tables.XOR)


if __name__ == '__main__':
    logging.basicConfig(filename='core.log', filemode='w', level=logging.DEBUG)
    unittest.main()
