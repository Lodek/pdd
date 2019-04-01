from blocks import *
from dl import Bus, BaseCircuit

class ALU(BaseCircuit):
    """
    
    """
    input_labels = "a b f".split()
    output_labels = "y".split()
    sizes = dict(f=3)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        #invert B if f[2] is set else B
        b_inverter = cb.SimpleMux(d0=i.b, d1=i.b, s=i.f[2], bubbles=['d1']) 
        b = b_inverter.y
        adder = cb.CPA(a=i.a, b=b, cin=i.f[2]) # A+B if f[2] is 0 else B-A 
        g1 = AND(a=i.a, b=b)
        g2 = OR(a=i.a, b=b)
        zero_extended_msb = Bus.gnd(len(adder.s) - 1) + adder.s[-1]
        output_select = cb.Mux(d0=g1.y, d1=g2.y, d2=adder.s, d3=zero_extended_msb, s=i.f[:2])
        self.set_outputs(y=output_select.y)
        

