#!/usr/bin/env python
import unittest
from pdd.dl import Bus
from pdd.tools import TruthTable, BaseCircuitTester
from blocks import *
       

class TestProcessor(BaseCircuitTester):

    def proc_reset(self, p):
        clk = p.clk
        p.r.set()
        clk.pulse()
        p.r.reset()
        clk.pulse()
        p.r.set()
        clk.pulse()
        p.r.reset()
        
    def test_lda(self):
        proc = Processor('lda-program.txt')
        clk = proc.clk
        self.proc_reset(proc)
        for i in range(100):
            print(i)
            clk.pulse()
            if int(proc.out.signal) == 3:
                self.assertTrue(True)
        
        
if __name__ == '__main__':
    unittest.main()
