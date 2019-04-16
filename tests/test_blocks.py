#!/usr/bin/env python
import base_tester
import unittest, logging
from dl import Bus
from blocks import *
import truth_tables
from tools import gen_output_table, TruthTable

class TestGate(unittest.TestCase):

    def _tester(self, circuit, truth_table):
        generated_table = TruthTable(circuit.input_labels, circuit.output_labels, 
                                     gen_output_table(circuit))
        self.assertEqual(truth_table, generated_table)
                
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

    def test_XNOR(self):
        g = XOR(bubbles=['y'])
        self._tester(g, truth_tables.XNOR)

    def test_NAND(self):
        g = AND(bubbles=['y'])
        self._tester(g, truth_tables.NAND)

    def test_NOR(self):
        g = OR(bubbles=['y'])
        self._tester(g, truth_tables.NOR)

    def test_SimpleMux(self):
        circuit = cb.SimpleMux()
        self._tester(circuit, truth_tables.SimpleMux)

    def test_BaseDecoder(self):
        circuit = cb.BaseDecoder()
        self._tester(circuit, truth_tables.BaseDecoder)

    def test_Decoder_one_input(self):
        circuit = cb.Decoder(1)
        self._tester(circuit, truth_tables.Decoder_1)

    def test_HalfAdder(self):
        circuit = cb.HalfAdder()
        self._tester(circuit, truth_tables.HalfAdder)

    def test_FullAdder(self):
        circuit = cb.FullAdder()
        self._tester(circuit, truth_tables.FullAdder)

    def test_3input_and(self):
        circuit = AND(inputs=3)
        self._tester(circuit, truth_tables.AND_3in)

class TestDecoder(unittest.TestCase):

    def test_decoder(self):
        circuit = cb.Decoder(size=3)
        

if __name__ == '__main__':
    logging.basicConfig(filename='core.log', filemode='w', level=logging.DEBUG)
    unittest.main()
