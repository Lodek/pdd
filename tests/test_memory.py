from dl import Bus, BaseCircuit
import blocks.sequential as sb
import unittest, logging

BaseCircuit.autoupdate = True


class TestROM(unittest.TestCase):

    def test_memory(self):
        """Test ROM by assigning directly to the bit cells"""
        words = 4
        rom = sb.ROM(words, ce=Bus.vdd(), size=2)
        signals = range(words)
        rom.burn(signals)
        for i in range(words):
            rom.addr = i
            self.assertEqual(int(rom.q.signal), i)

    
class TestMemoryCell(unittest.TestCase):

    def test_cell(self):
        """Test memory cell by testing that it can be written to,
        read and that tristate work"""
        cell = sb.MemoryCell(size=4)
        cell.auto_update = True
        cell.w.set()
        cell.en.set()
        cell.d=7
        cell.clk.pulse()
        self.assertEqual(int(cell.q.signal), 7)
        cell.w.reset()
        cell.d=3
        cell.clk.pulse()
        self.assertEqual(int(cell.q.signal), 7)

class TestRAM(unittest.TestCase):

    def test_ram(self):
        """Test 4x4 memory array"""
        ram = sb.RAM(4, size=2)
        ram.d = 0xf
        ram.addr=1
        ram.w.set()
        ram.en.set()
        ram.clk.pulse()
        self.assertEqual(int(ram.q.signal), 0xf)
        ram.w.reset()
        ram.d=1
        ram.clk.pulse()
        self.assertEqual(int(ram.q.signal), 0xf)
        ram.addr=0
        self.assertEqual(int(ram.q.signal), 0)

        
if __name__ == '__main__':
    logging.basicConfig(filename=__file__+'.txt', filemode='w', level=logging.DEBUG)
    unittest.main()
