"""
Sequential Logic building blocks
"""
from core import Signal
from dl import BaseCircuit


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
        
