"""
Sequential Logic building blocks
"""

import pdd.combinational_blocks as cb
from pdd.gates import *
from pdd.dl import BaseCircuit, Bus

class SRLatch(BaseCircuit):
    """
    Classic SRLatch implementation using 2 NOR gates cross connected.
    SRLatches are the fundamental building block of Sequential circuits.
    """
    input_labels = 's r'.split()
    output_labels = 'q q_bar'.split()

    def make(self):
        i = self.get_inputs()
        q_or = OR(a=i.r, bubbles=['y'])
        q_bar_or = OR(a=i.s, b=q_or.y, bubbles=['y'])
        q_or.connect(b=q_bar_or.y)
        self.set_outputs(q=q_or.y, q_bar=q_bar_or.y)
      

class DLatch(BaseCircuit):
    """
    DLatch adds combinational logic to the SRLatch to make it more useful.
    When clk is high the signal at d is propagated to q, else q is unchaged.
    clk bus must be of size 1
    """
    input_labels = 'd clk'.split()
    output_labels = ['q']
    sizes = dict(clk=1)

    def make(self):
        i = self.get_inputs()
        clk = i.clk.branch(i.d)
        reset_gate = AND(a=clk, b=i.d, bubbles=['b'])
        set_gate = AND(a=clk, b=i.d)
        sr = SRLatch(s=set_gate.y, r=reset_gate.y)
        self.set_outputs(q=sr.q)
        
        
class DFlipFlop(BaseCircuit):
    """
    In practice DLatches aren't used often. If d changes while clk is high, the
    change propagates to q. FlipFlops only propagate d to q at the 
    rising edge of the clock.
    """
    input_labels = 'd clk'.split()
    output_labels = ['q']
    sizes = dict(clk=1)

    def make(self):
        i = self.get_inputs()
        l1 = DLatch(d=i.d, clk=i.clk, bubbles=['clk'])
        l2 = DLatch(d=l1.q, clk=i.clk)
        self.set_outputs(q=l2.q)
                    

class FlipFlop(BaseCircuit):
    """
    There are many variations of flip flops. Resetable flip flops, enable flip flops,
    tri-stated output flipflops. This impelementation implements all of the above.
    e and l are active low, r is active high
    """
    input_labels = "r e clk l d".split()
    output_labels = "q".split()
    sizes = dict(r=1, e=1, clk=1, l=1)

    def make(self):
        i = self.get_inputs()
        #have nice defaults without user intervention
        inverter = OR(a=i.l+i.e, b=Bus.gnd(2), bubbles = ['y'])
        e, l = inverter.y[0], inverter.y[1]
        l_mux = cb.BaseMux(d1=i.d, s=l)
        reset_mux = cb.BaseMux(d0=l_mux.y, d1=Bus.gnd(l_mux.y), s=i.r)
        dflip = DFlipFlop(d=reset_mux.y, clk=i.clk)
        l_mux.connect(d0=dflip.q)
        self.set_tristate(q=e)
        self.set_outputs(q=dflip.q)

        
class Counter(BaseCircuit):
    """
    
    """
    input_labels = "clk r".split()
    output_labels = "q".split()
    sizes = dict(clk=1, r=1)

    def make(self):
        i = self.get_inputs()
        word_size = len(i.q)
        flip = FlipFlop(size=word_size, clk=i.clk, r=i.r)
        b_bus = Bus.gnd(word_size -1) + Bus.vdd()
        adder = cb.CPA(a=flip.q, b=b_bus)
        flip.connect(d=adder.s)
        self.set_outputs(q=flip.q)
       

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


class RAM(BaseCircuit):
    """
    Word adressable RAM implementation.
    w and ce are high active.
    """
    input_labels = "d clk addr w ce".split()
    output_labels = "q".split()
    def __init__(self, word_size, **kwargs):
        self.word_size = word_size
        self.sizes = dict(ce=1, clk=1, w=1, q=word_size, d=word_size)
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        self.set_tristate(q=i.ce)
        #cells have active low enable
        addr_lines = cb.Decoder(a=i.addr, e=Bus.vdd())
        cells = [FlipFlop(clk=i.clk, d=i.d, e=en_bus, q=i.q, bubbles=['e']) for en_bus in addr_lines.y]
        write_gates = [AND(a=i.w, b=bus, bubbles=['y']) for bus in addr_lines.y]
        for gate, cell in zip(write_gates, cells):
            cell.connect(l=gate.y)
