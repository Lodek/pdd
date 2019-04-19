import base_tester
from pdd.dl import Bus, BaseCircuit
from pdd.blocks import *
import unittest, logging
from pdd.core import Wire
from pdd.tools import BaseCircuitTester

Wire.auto_update = True


class TestROM(BaseCircuitTester):

    def test_memory(self):
        """Test ROM by assigning directly to the bit cells"""
        words = 4
        rom = cb.ROM(words, ce=Bus.vdd(), size=2)
        signals = range(words)
        rom.burn(signals)
        for i in range(words):
            rom.addr = i
            self.assertEqual(int(rom.q.signal), i)

    
class TestRAM(BaseCircuitTester):

    def test_ram(self):
        """Test 4x4 memory array"""
        ram = sb.RAM(4, size=2)
        clk = ram.clk
        ram.d = 0xf
        ram.addr = 1
        ram.w.set()
        ram.ce.set()
        clk.pulse()
        self.assertEqual(int(ram.q.signal), 0xf)
        ram.w.reset()
        ram.d=1
        ram.clk.pulse()
        self.assertEqual(int(ram.q.signal), 0xf)
        ram.addr=0
        self.assertEqual(int(ram.q.signal), 0)

        
if __name__ == '__main__':
    unittest.main()
