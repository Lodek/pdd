from blocks import *
from dl import Bus, BaseCircuit

class ALU(BaseCircuit):
    """
    
    """
    input_labels = "a b sub e".split()
    output_labels = "s".split()
    sizes = dict(e=1, sub=1)

    def make(self):
        i = self.get_inputs()
        #Mux controls whether B should be negated or not
        select_b = cb.SimpleMux(a0=i.b, a1=i.b, s=i.sub, bubbles=['b'])
        adder = cb.CPA(a=i.a, b=select_b.y, cin=i.sub)
        self.set_tristate(s=i.e)
        self.set_outputs(s=adder.s)

class RingCounter(BaseCircuit):
    """
    
    """
    input_labels = "clk".split()
    output_labels = "t0 t1 t2 t3 t4 t5".split()
    sizes = dict(clk=1, t0=1, t1=1, t2=1, t3=1, t4=1, t5=1)

    def make(self):
        i = self.get_inputs()
        counter = sb.Counter(size=3, clk=i.clk)
        adder = cb.CPA(a=Bus(3, 2), b=counter.q)
        dec = cb.Decoder(a=adder.s, e=Bus.vdd())
        self.set_outputs(t0=dec.y2, t1=dec.y3, t2=dec.y4, t3=dec.y5, t4=dec.y6, t5=dec.y7)

class SettableCounter(BaseCircuit):
    """
    
    """
    input_labels = "d l clr clk".split()
    output_labels = "q".split()
    sizes = dict(l=1, clr=1, clk=1)

    def make(self):
        i = self.get_inputs()
        word_size = len(i.d)
        mux = SimpleMux(a1=i.d, s=i.l)
        flip = ResetFlipFlop(d=mux.y clk=i.clk, reset=i.clr)
        adder = cb.CPA(a=flip.q, b=Bus(word_size, 1))
        mux.connect(a0=adder.s)
        self.set_outputs(q=flip.q)

