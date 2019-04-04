"""
Sequential Logic building blocks
"""
from dl import BaseCircuit, Bus
from blocks.combinational import AND, OR, XOR
import blocks.combinational as cb

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
                    

class EnableFlipFlop(BaseCircuit):
    """
    
    """
    input_labels = 'd clk en'.split()
    output_labels = ['q']
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        en_and = AND(a=i.en, b=i.clk)
        flip = DFlipFlop(d=i.d, clk=en_and.y)
        self.set_outputs(q=flip.q)

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


class REFlipFlop(BaseCircuit):
    """
    
    """
    input_labels = "d clk reset en".split()
    output_labels = "q".split()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        select_and = AND(inputs=3, a0=i.d, a1=i.en, a2=a.reset)
        flip = DFlipFlop(d=i.d, clk=en_and.y)
        self.set_outputs(q=flip.q)
        

        
class Counter(BaseCircuit):
    """
    
    """
    input_labels = "clk reset".split()
    output_labels = "q".split()
    sizes = dict(clk=1, reset=1)
    def __init__(self, word_size, **kwargs):
        self.word_size = word_size
        self.sizes.update({'q':word_size})
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        flip = ResetFlipFlop(size=self.word_size, clk=i.clk, reset=i.reset)
        b_bus = Bus.gnd(self.word_size -1) + Bus.vdd()
        adder = cb.CPA(a=flip.q, b=b_bus)
        flip.connect(d=adder.s)
        self.set_outputs(q=flip.q)
       

class ROM(BaseCircuit):
    """
    
    """
    input_labels = "addr clk en".split()
    output_labels = "q".split()
    def __init__(self, word_size, **kwargs):
        self.word_size = word_size
        self.sizes = dict(q=word_size, en=1, clk=1)
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        q_bus = self.terminals['q'].a
        addr_decoder = cb.Decoder(a=i.addr, e=Bus.vdd())
        self.set_tristate(q=i.en)
        words = len(addr_decoder.y)
        self.registers = [DFlipFlop(clk=i.clk, size=self.word_size) for _ in range(words)]
        for flip, bus in zip(self.registers, addr_decoder.y):
            flip.set_tristate(q=bus)
            flip.connect(q=q_bus)
       


class BitCell(BaseCircuit):
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
        flip.set_tristate(q=i.en)
        self.set_outputs(q=flip.q)

        
class RAM(BaseCircuit):
    """
    
    """
    input_labels = "d clk addr w en".split()
    output_labels = "q".split()
    def __init__(self, word_size, **kwargs):
        self.word_size = word_size
        self.sizes = dict(q=word_size, en=1, clk=1, w=1, d=word_size)
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        self.set_tristate(q=i.en)
        addr_lines = cb.Decoder(a=i.addr, e=Bus.vdd())
        cells = [BitCell(clk=i.clk, d=i.d, en=en_bus, q=i.q) for en_bus in addr_lines.y]
        write_lines = cb.Decoder(a=i.addr, e=Bus.vdd())
        write_gates = [AND(a=i.w, b=bus) for bus in write_lines.y]
        for gate, cell in zip(write_gates, cells):
            cell.connect(w=gate.y)
