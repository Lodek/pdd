#!/usr/bin/env python
import unittest
from pdd.dl import Bus
from pdd.tools import TruthTable, BaseCircuitTester
from blocks import *

class TestSapBlocks(BaseCircuitTester):

    def test_alu(self):
        circ = ALU(size=4)
        circ.a = 3
        circ.b = 2
        self.assertSigEq(circ.s, 5)
        circ.sub.set()
        self.assertSigEq(circ.s, 1)
        circ.e.set()
        circ.b = 0
        self.assertSigEq(circ.s, 1)
        
    def test_double_flip(self):
        circ = DoubleFlipFlop(size=4)
        clk = circ.clk
        circ.r.set()
        clk.pulse()
        self.assertSigEq(circ.q, 0)
        self.assertSigEq(circ.qt, 0)
        circ.r.reset()
        circ.d = 2
        clk.pulse()
        self.assertSigEq(circ.q, 2)
        self.assertSigEq(circ.qt, 2)
        circ.l.set()
        circ.d = 3
        clk.pulse()
        self.assertSigEq(circ.q, 2)
        self.assertSigEq(circ.qt, 2)
        circ.l.reset()
        circ.e.set()
        clk.pulse()
        self.assertSigEq(circ.q, 3)
        self.assertSigEq(circ.qt, 2)



class TestCU(BaseCircuitTester):
    
    def setUp(self):
        self.inst_d = dict(lda=0, add=1, sub=2, out=0xd)
        self.nop_state = dict(lo=1, lb=1, eu=1, su=0, ea=1, la=1, ei=1, li=1, ce=0, lm=1, ep=1, cp=0)
        self.fetch_flags = ['ep lm', 'cp', 'ce li']
        self.lda_flags = ['ei lm', 'ce la', '']
        self.add_flags = ['ei lm', 'ce lb', 'eu la']
        self.sub_flags = ['ei lm', 'ce lb su', 'eu la su']
        self.out_flags = ['ea lo', '', '']

        self.cu = ControlUnit()

    def test_lda(self):
        clk = self.cu.clk
        self.cu.d = self.inst_d['lda']
        self.cu.r.set()
        clk.pulse()
        self.cu.r.reset()
        self.assertFlags(self.fetch_flags[0])
        clk.pulse()
        self.assertFlags(self.fetch_flags[1])
        clk.pulse()
        self.assertFlags(self.fetch_flags[2])
        clk.pulse()
        self.assertFlags(self.lda_flags[0])
        clk.pulse()
        self.assertFlags(self.lda_flags[1])
        clk.pulse()
        self.assertFlags(self.lda_flags[2])
        clk.pulse()
        self.assertFlags(self.fetch_flags[0])

    def test_add(self):
        clk = self.cu.clk
        self.cu.d = self.inst_d['add']
        self.cu.r.set()
        clk.pulse()
        self.cu.r.reset()
        self.assertFlags(self.fetch_flags[0])
        clk.pulse()
        self.assertFlags(self.fetch_flags[1])
        clk.pulse()
        self.assertFlags(self.fetch_flags[2])
        clk.pulse()
        self.assertFlags(self.add_flags[0])
        clk.pulse()
        self.assertFlags(self.add_flags[1])
        clk.pulse()
        self.assertFlags(self.add_flags[2])
        clk.pulse()
        self.assertFlags(self.fetch_flags[0])

    def test_sub(self):
        clk = self.cu.clk
        self.cu.d = self.inst_d['sub']
        self.cu.r.set()
        clk.pulse()
        self.cu.r.reset()
        self.assertFlags(self.fetch_flags[0])
        clk.pulse()
        self.assertFlags(self.fetch_flags[1])
        clk.pulse()
        self.assertFlags(self.fetch_flags[2])
        clk.pulse()
        self.assertFlags(self.sub_flags[0])
        clk.pulse()
        self.assertFlags(self.sub_flags[1])
        clk.pulse()
        self.assertFlags(self.sub_flags[2])
        clk.pulse()
        self.assertFlags(self.fetch_flags[0])

    def test_out(self):
        clk = self.cu.clk
        self.cu.d = self.inst_d['out']
        self.cu.r.set()
        clk.pulse()
        self.cu.r.reset()
        self.assertFlags(self.fetch_flags[0])
        clk.pulse()
        self.assertFlags(self.fetch_flags[1])
        clk.pulse()
        self.assertFlags(self.fetch_flags[2])
        clk.pulse()
        self.assertFlags(self.out_flags[0])
        clk.pulse()
        self.assertFlags(self.out_flags[1])
        clk.pulse()
        self.assertFlags(self.out_flags[2])
        clk.pulse()
        self.assertFlags(self.fetch_flags[0])


    def assertFlags(self, flags):
        state = self.gen_state_from_flags(flags)
        match = self.compare_circ_state(self.cu, state)
        self.assertTrue(match)
        
    def gen_state_from_flags(self, flags):
        state = dict(self.nop_state)
        invert_state = lambda x : 0 if x else 1
        for f in flags.split():
            state[f] = invert_state(state[f])
        return state

        
    def compare_circ_state(self, cu, state):
        """Compare whether the cu's state match the given state.
        Compare does so by calling cu.state_int and removing the keys
        associated to inputs"""
        cu_state = cu.state_int
        for l in cu.input_labels:
            cu_state.pop(l)
        return True if cu_state == state else False
        

    
        
if __name__ == '__main__':
    unittest.main()
