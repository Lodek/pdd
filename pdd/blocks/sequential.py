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
