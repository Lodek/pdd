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

    def assertSigEq(self, bus, n):
        self.assertEqual(int(bus.signal), n)

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
        self._tester(circuit, truth_tables.BaseMux)

    def test_BaseDecoder(self):
        circuit = BaseDecoder()
        self._tester(circuit, truth_tables.BaseDecoder)

    def test_Mux_base_case(self):
        circuit = Mux(1, size=1)
        self._tester(circuit, truth_tables.BaseMux)

    def test_Mux(self):
        mux = Mux(2, size=2)
        for i in range(4):
            mux.get_bus('d'+str(i)).signal = i
        gen = SignalGen.sweep(dict(s=mux.s))
        for i, _ in enumerate(gen.iterate()):
            self.assertEqual(int(mux.y.signal), i)
        

        

class ArithmeticCircuit(BaseCircuitTester):

    def test_HalfAdder(self):
        circuit = HalfAdder()
        self._tester(circuit, truth_tables.HalfAdder)

    def test_FullAdder(self):
        circuit = FullAdder()
        self._tester(circuit, truth_tables.FullAdder)

    def test_cpa(self):
        adder = CPA(size=4)
        adder.a = 3
        adder.b = 4
        self.assertEqual(int(adder.s.signal), 7)
        adder.cin.set()
        self.assertEqual(int(adder.s.signal), 8)
        adder.a = 0xf
        adder.b = 0
        self.assertEqual(int(adder.s.signal), 0)
        self.assertEqual(int(adder.cout.signal), 1)

    def test_subtractor(self):
        circuit = Subtractor(size=4)
        circuit.a = 4
        circuit.b = 3
        self.assertEqual(int(circuit.s.signal), 1)
        circuit.a = 3
        circuit.b = 4
        self.assertEqual(int(circuit.s.signal), 0xf)


    def test_eq_comp(self):
        circ = EqualityComparator(size=4)
        circ.a = 3
        circ.b = 4
        self.assertSigEq(circ.eq, 0)
        circ.b = 3
        self.assertSigEq(circ.eq, 1)

    def test_comp(self):
        circ = Comparator(size=4)
        #case a < b
        circ.a = 1
        circ.b = 2
        self.assertSigEq(circ.eq, 0)
        self.assertSigEq(circ.neq, 1)
        self.assertSigEq(circ.lte, 1)
        self.assertSigEq(circ.lt, 1)
        self.assertSigEq(circ.gt, 0)
        self.assertSigEq(circ.gte, 0)
        #case a > b
        circ.a = 3
        circ.b = 0
        self.assertSigEq(circ.eq, 0)
        self.assertSigEq(circ.neq, 1)
        self.assertSigEq(circ.lte, 0)
        self.assertSigEq(circ.lt, 0)
        self.assertSigEq(circ.gt, 1)
        self.assertSigEq(circ.gte, 1)
        #case a=b
        circ.a = 2
        circ.b = 2
        self.assertSigEq(circ.eq, 1)
        self.assertSigEq(circ.neq, 0)
        self.assertSigEq(circ.lte, 1)
        self.assertSigEq(circ.lt, 0)
        self.assertSigEq(circ.gt, 0)
        self.assertSigEq(circ.gte, 1)
        


if __name__ == '__main__':
    #logging.basicConfig(filename='core.log', filemode='w', level=logging.DEBUG)
    unittest.main()
