#!/usr/bin/env python
import base_tester
from base_tester import BaseCircuitTester
import unittest, logging
from blocks.sequential import *
from tools import TruthTable, SignalGen
import truth_tables
from core import Wire

Wire.auto_update = True

class TestSequentialBase(BaseCircuitTester):

    def test_srlatch(self):
        """Test SR Latch with 2 bit input"""
        circ = SRLatch(size=2)
        circ.s.pulse()
        self.assertSigEq(circ.q, 3)
        circ.r.pulse()
        self.assertSigEq(circ.q, 0)
        
    def test_dlatch(self):
        """Test DLatch circuit with a 2 bit input"""
        circ = DLatch(size=2)
        circ.clk.pulse()
        self.assertSigEq(circ.q, 0)
        circ.d = 3
        self.assertSigEq(circ.q, 0)
        circ.clk.set()
        self.assertSigEq(circ.q, 3)
        circ.d = 2
        self.assertSigEq(circ.q, 2)

    def test_dflipflop(self):
        """Test flipflop conditions. Signal propagation only at the rising edge"""
        circ = DFlipFlop(size=2)
        circ.clk.pulse()
        self.assertSigEq(circ.q, 0)
        circ.d = 3
        self.assertSigEq(circ.q, 0)
        circ.clk.set()
        self.assertSigEq(circ.q, 3)
        circ.d = 2
        self.assertSigEq(circ.q, 3)

    def test_flipflop(self):
        """Test ELR flip flop"""
        circ = FlipFlop(size=2)
        #test basic flip flop functionality
        circ.d = 3
        self.assertSigEq(circ.q, 0)
        circ.clk.pulse()
        self.assertSigEq(circ.q, 3)
        #test reset circuit
        circ.r.set()
        circ.clk.pulse()
        self.assertSigEq(circ.q, 0)
        circ.r.reset()
        #test load
        circ.l.set()
        circ.d = 3
        circ.clk.pulse()
        self.assertSigEq(circ.q, 0)
        #test enable
        circ.l.reset()
        circ.e.set()
        circ.clk.pulse()
        self.assertSigEq(circ.q, 0)
       
        
class TestSequentialBlocks(BaseCircuitTester):

    def test_counter(self):
        circ = Counter(size=4)
        clk = circ.clk
        circ.r.set()
        clk.pulse()
        circ.r.reset()
        self.assertSigEq(circ.q, 0)
        for i in range(2**4):
            self.assertSigEq(circ.q, i)
            clk.pulse()
        self.assertSigEq(circ.q, 0)
    
if __name__ == '__main__':
    #logging.basicConfig(filename='core.log', filemode='w', level=logging.DEBUG)
    unittest.main()
