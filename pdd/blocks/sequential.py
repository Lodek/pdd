"""
Sequential Logic building blocks
"""
from blocks.combinational import AND, OR, XOR
import blocks.combinational as cb
from dl import BaseCircuit, Bus
import tools

class SRLatch(BaseCircuit):
    """
    
    """
    input_labels = 's r'.split()
    output_labels = 'q q_bar'.split()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        q_or = OR(a=i.r, bubbles=['y'])
        q_bar_or = OR(a=i.s, b=q_or.y, bubbles=['y'])
        q_or.connect(b=q_bar_or.y)
        self.set_outputs(q=q_or.y, q_bar=q_bar_or.y)
      

class DLatch(BaseCircuit):
    """
    
    """
    input_labels = 'd clk'.split()
    output_labels = ['q']
    sizes = dict(clk=1)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        clk = i.clk.branch(self.sizes['d'])
        reset_gate = AND(a=clk, b=i.d, bubbles=['b'])
        set_gate = AND(a=clk, b=i.d)
        sr = SRLatch(s=set_gate.y, r=reset_gate.y)
        self.set_outputs(q=sr.q)
        
        
class DFlipFlop(BaseCircuit):
    """
    
    """
    input_labels = 'd clk'.split()
    output_labels = ['q']
    sizes = dict(clk=1)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        l1 = DLatch(d=i.d, clk=i.clk, bubbles=['clk'])
        l2 = DLatch(d=l1.q, clk=i.clk)
        self.set_outputs(q=l2.q)
                    

class ResetFlipFlop(BaseCircuit):
    """
    
    """
    input_labels = "d clk reset".split()
    output_labels = "q".split()
    sizes = dict(clk=1, reset=1)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        reset_bus = i.reset.branch(len(i.d))
        reset_gate = AND(a=i.d, b=reset_bus, bubbles=['b'])
        flip = DFlipFlop(d=reset_gate.y, clk=i.clk)
        self.set_outputs(q=flip.q)


class ELFlipFlop(BaseCircuit):
    """
    
    """
    input_labels = "d clk l e".split()
    output_labels = "q".split()
    sizes = dict(clk=1, l=1, e=1)
    def make(self):
        i = self.get_inputs()
        select_mux = cb.SimpleMux(s=i.l, d1=i.d)
        flip = DFlipFlop(d=select_mux.y, clk=i.clk)
        select_mux.connect(a0=flip.q)
        self.set_tristate(q=i.e)
        self.set_outputs(q=flip.q)
        

        
class Counter(BaseCircuit):
    """
    
    """
    input_labels = "clk reset".split()
    output_labels = "q".split()
    sizes = dict(clk=1, reset=1)

    def make(self):
        i = self.get_inputs()
        word_size = len(i.q)
        flip = ResetFlipFlop(size=word_size, clk=i.clk, reset=i.reset)
        b_bus = Bus.gnd(word_size -1) + Bus.vdd()
        adder = cb.CPA(a=flip.q, b=b_bus)
        flip.connect(d=adder.s)
        self.set_outputs(q=flip.q)
       

class ROM(BaseCircuit):
    """
    Implementation of ROM. Use burn_rom method to assign values to rom.
    Takes the memory word size as a parameter. The number of words in ROM is
    give by the size of the addr bus.
    """
    input_labels = "addr ce".split()
    output_labels = "q".split()
    def __init__(self, word_size, **kwargs):
        self.word_size = word_size
        self.sizes = dict(q=word_size, ce=1)
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        W_bus = i.q
        addr_decoder = cb.Decoder(a=i.addr, e=Bus.vdd())
        self.set_tristate(q=i.ce)
        words = len(addr_decoder.y)
        self.cells = [OR(size=self.word_size) for _ in range(words)]
        for cell, bus in zip(self.cells, addr_decoder.y):
            cell.set_tristate(y=bus)
            cell.connect(y=W_bus)

    def fburn(self, f):
        """Call IOHelper on f to open a file and get the memory contents
        then burn the rom with the words in f"""
        words = tools.IOHelper.parse_memory(f)
        self.burn(words)
        
    def burn(self, contents):
        """Assign word in contents sequentially to memory cells"""
        for word, cell in zip(contents, self.cells):
            cell.a = word


class MemoryCell(BaseCircuit):
    """
    
    """
    input_labels = "d clk w en".split()
    output_labels = "q".split()
    sizes = dict(clk=1, w=1, en=1)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        mux = cb.SimpleMux(s=i.w, d1=i.d)
        mux.connect(d0=mux.y)
        flip = DFlipFlop(d=mux.y, clk=i.clk)
        self.set_tristate(q=i.en)
        self.set_outputs(q=flip.q)

        
class RAM(BaseCircuit):
    """
    
    """
    input_labels = "d clk addr w en".split()
    output_labels = "q".split()
    sizes = dict(en=1, clk=1, w=1)
    def __init__(self, word_size, **kwargs):
        self.word_size = word_size
        self.sizes.update(q=word_size, d=word_size)
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        self.set_tristate(q=i.en)
        addr_lines = cb.Decoder(a=i.addr, e=Bus.vdd())
        cells = [MemoryCell(clk=i.clk, d=i.d, en=en_bus, q=i.q) for en_bus in addr_lines.y]
        write_gates = [AND(a=i.w, b=bus) for bus in addr_lines.y]
        for gate, cell in zip(write_gates, cells):
            cell.connect(w=gate.y)

class SettableCounter(BaseCircuit):
    """
    
    """
    input_labels = "d l clr clk".split()
    output_labels = "q".split()
    sizes = dict(l=1, clr=1, clk=1)

    def make(self):
        i = self.get_inputs()
        word_size = len(i.d)
        mux = cb.SimpleMux(d1=i.d, s=i.l)
        flip = sb.ResetFlipFlop(d=mux.y, clk=i.clk, reset=i.clr)
        adder = cb.CPA(a=flip.q, b=Bus(word_size, 1))
        mux.connect(d0=adder.s)
        self.set_outputs(q=flip.q)

