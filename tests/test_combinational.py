#!/usr/bin/env python
import base_tester
import unittest, logging
from blocks.combinational import *
from tools import TruthTable, SignalGen
import truth_tables
from core import Wire

Wire.auto_update = True

class BaseCircuitTester(unittest.TestCase):
    def _tester(self, circuit, truth_table):
        gen = SignalGen.sweep_circuit(circuit)
        states = [circuit.state_int for _ in gen.iterate()]
        generated_table = TruthTable(states)
        self.assertEqual(truth_table, generated_table)


class TestGate(BaseCircuitTester):
               
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

    def test_3input_and(self):
        circuit = AND(inputs=3)
        self._tester(circuit, truth_tables.AND_3in)


class TestCombinationalBlocks(BaseCircuitTester):

    def test_BaseMux(self):
        circuit = BaseMux()
        self._tester(circuit, truth_tables.SimpleMux)

    def test_BaseDecoder(self):
        circuit = BaseDecoder()
        self._tester(circuit, truth_tables.BaseDecoder)


class ArithmeticCircuit(BaseCircuitTester):

    def test_HalfAdder(self):
        circuit = HalfAdder()
        self._tester(circuit, truth_tables.HalfAdder)

    def test_FullAdder(self):
        circuit = FullAdder()
        self._tester(circuit, truth_tables.FullAdder)


if __name__ == '__main__':
    #logging.basicConfig(filename='core.log', filemode='w', level=logging.DEBUG)
    unittest.main()
