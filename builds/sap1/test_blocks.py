#!/usr/bin/env python
import unittest
from pdd.dl import Bus
from pdd.tools import TruthTable, BaseCircuitTester, Inspector
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
        self.inst_d = dict(lda=0, add=1, sub=2, out=0xe)
        self.nop_state = dict(lo=1, lb=1, eu=1, su=0, ea=1, la=1, ei=1, li=1, ce=0, lm=1, ep=1, cp=0)
        self.fetch_flags = ['ep lm', 'cp', 'ce li']
        self.lda_flags = ['ei lm', 'ce la', '']
        self.add_flags = ['ei lm', 'ce lb', 'eu la']
        self.sub_flags = ['ei lm', 'ce lb su', 'eu la su']
        self.out_flags = ['ea lo', '', '']

        self.cu = ControlUnit()
        self.cu.ic = 1
        self.cu.ic = 0

    def test_lda(self):
        self.cu.d = self.inst_d['lda']
        for i, mi in enumerate(self.fetch_flags):
            self.cu.ic = i
            self.assertFlags(mi)
        for i, mi in enumerate(self.lda_flags):
            self.cu.ic = i + 3
            self.assertFlags(mi)

    def test_add(self):
        self.cu.d = self.inst_d['add']
        for i, mi in enumerate(self.fetch_flags):
            self.cu.ic = i
            self.assertFlags(mi)
        for i, mi in enumerate(self.add_flags):
            self.cu.ic = i + 3
            self.assertFlags(mi)

    def test_sub(self):
        self.cu.d = self.inst_d['sub']
        for i, mi in enumerate(self.fetch_flags):
            self.cu.ic = i
            self.assertFlags(mi)
        for i, mi in enumerate(self.sub_flags):
            self.cu.ic = i + 3
            self.assertFlags(mi)

    def test_out(self):
        self.cu.d = self.inst_d['out']
        for i, mi in enumerate(self.fetch_flags):
            self.cu.ic = i
            self.assertFlags(mi)
        for i, mi in enumerate(self.out_flags):
            self.cu.ic = i + 3
            self.assertFlags(mi)

    def assertFlags(self, flags):
        """DRY for the process of comparing the state of CU with the 
        expected state given the flags that are to be changed"""
        state = self.gen_state_from_flags(flags)
        match = self.compare_circ_state(self.cu, state)
        self.assertTrue(match)
        
    def gen_state_from_flags(self, flags):
        """From the nop state dictionary return a dictionary
        with the value of each flag in flags inverted"""
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
        

class TestStateArchitectureUnit(BaseCircuitTester):

    def setUp(self):
        self.sa = StateArchitectureUnit()
        self.sa.init_flags_nop()
        self.sa.reset()
        
    def test_win(self):
        sa = self.sa
        sa.win = 69
        self.assertSigEq(sa.wout, 0)
        sa.lwin.set()
        self.assertSigEq(sa.wout, 69)

    def test_pc(self):
        sa = self.sa
        clk = sa.clk
        #test that counter won't increment without cp
        clk.pulse()
        sa.ep = 0
        self.assertSigEq(sa.wout, 0)
        sa.cp.set()
        clk.pulse()
        self.assertSigEq(sa.wout, 1)
        clk.pulse()
        self.assertSigEq(sa.wout, 2)

    def test_acc(self):
        sa = self.sa
        clk = sa.clk
        #load acc and resets win
        sa.lwin.set()
        sa.la = 0
        sa.win = 10
        clk.pulse()
        sa.lwin.reset()
        sa.la = 1
        sa.win = 0
        #outputs acc
        sa.ea = 0
        clk.pulse()
        self.assertSigEq(sa.wout, 10)

    def test_alu(self):
        sa = self.sa
        clk = sa.clk
        #load value into acc
        sa.win, sa.lwin, sa.la = 69, 1, 0
        clk.pulse()
        sa.win, sa.la = 0, 0
        sa.lwin = 0
        sa.eu = 0
        self.assertSigEq(sa.wout, 69)
        
    def test_out_reg(self):
        sa = self.sa
        clk = sa.clk
        #load W bus
        sa.win, sa.lwin, sa.lo = 3, 1, 0
        clk.pulse()
        self.assertSigEq(sa.out, 3)

    def test_rom_mar(self):
        sa = self.sa
        sa.load_program('test_program.txt')
        clk = sa.clk
        #load mar
        sa.win, sa.lwin, sa.lm = 3, 1, 0
        clk.pulse()
        sa.lwin, sa.lm = 0, 1
        sa.ce = 1
        self.assertSigEq(sa.wout, 4)

    def test_ir(self):
        sa = self.sa
        clk = sa.clk
        #load ir
        sa.win, sa.li, sa.lwin = 3, 0, 1
        clk.pulse()
        sa.win, sa.li = 0, 1
        self.assertSigEq(sa.wout, 0)
        sa.lwin, sa.ei = 0, 0
        self.assertSigEq(sa.wout, 3)
        self.assertSigEq(sa.iw, 3)
        
   
class TestProcessor(BaseCircuitTester):

    def setUp(self):
        self.p = Processor()
        self.p.reset()
        self.insp = Inspector(dict(p=self.p, sa=self.p.sa, acc=self.p.sa.acc, out=self.p.sa.out_reg))
        
    def test_p1(self):
        """Simple LDA program to test the most basic of operations"""
        self.p.load_rom('p1.txt')
        for i in range(15):
            self.insp.inspect()
            print(i)
            if int(self.p.out.signal) == 3:
                self.assertTrue(True)
                break
            self.p.clk.pulse()
        else:
            self.assertTrue(False)

    def test_p2(self):
        self.p.load_rom('p2.txt')
        for i in range(13):
            self.insp.inspect()
            print(i)
            if int(self.p.out.signal) == 3:
                self.assertTrue(True)
                break
            self.p.clk.pulse()
        else:
            import pdb; pdb.set_trace()
            self.assertTrue(False)



        
if __name__ == '__main__':
    unittest.main()
