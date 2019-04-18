#!/usr/bin/env python
path_to_codebase = '../../pdd'
sys.path.append(path_to_codebase)
import base_tester
import unittest, logging
from dl import Bus
from blocks import *
import truth_tables
from tools import gen_output_table, TruthTable

class TestSapBlocks(BaseCircuitTester):

    def test_alu(self):
        circ = ALU(size=4)
        circ.e.set()
        circ.a = 3
        circ.b = 2
        self.assertSigEq(circ.s, 5)
        circ.sub.set()
        self.assertSigEq(circ.s, 1)
        circ.e.reset()
        circ.b = 0
        self.assertSigEq(circ.s, 1)
        
    def test_double_flip(self):
        circ = DoubleFlipFlop(size=4)
        clk = circ.clk
        circ.r.set()
        clk.pulse()
        self.AssertSigEq(circ.q, 0)
        self.AssertSigEq(circ.qt, 0)
        circ.d = 2
        clk.pulse()
        self.AssertSigEq(circ.q, 2)
        self.AssertSigEq(circ.qt, 2)
        circ.l.set()
        circ.d = 3
        clk.pulse()
        self.AssertSigEq(circ.q, 2)
        self.AssertSigEq(circ.qt, 2)
        circ.l.reset()
        circ.e.set()
        clk.pulse()
        self.AssertSigEq(circ.q, 3)
        self.AssertSigEq(circ.qt, 2)

    
        

        


if __name__ == '__main__':
    logging.basicConfig(filename='core.log', filemode='w', level=logging.DEBUG)
    unittest.main()
