import pdd.combinational_blocks as cb
from pdd.gates import *
import pdd.sequential_blocks as sb
from pdd.dl import Bus, BaseCircuit

class ALU(BaseCircuit):
    """
    Simple ALU with addition and subtraction. Tristated output, 
    tristate is low-active (ie e signal 1 laves s at high Z).
    """
    input_labels = "a b sub e".split()
    output_labels = "s".split()
    sizes = dict(e=1, sub=1)
    def make(self):
        i = self.get_inputs()
        #Mux controls whether B should be negated or not
        select_b = cb.BaseMux(d0=i.b, d1=i.b, s=i.sub, bubbles=['d1'])
        adder = cb.CPA(a=i.a, b=select_b.y, cin=i.sub)
        not_e = INV(a=i.e).y
        self.set_tristate(s=not_e)
        self.set_outputs(s=adder.s)


class DoubleFlipFlop(BaseCircuit):
    """
    FlipFlop with two outputs. q is normal output and qt is tristated.
    qt tristate is low-active (ie. e signal 1 leaves qt at Z).
    l is low active
    r is high active and synchronous
    """
    input_labels = "d e l clk r".split()
    output_labels = "q qt".split()
    sizes = dict(e=1, l=1, clk=1, r=1)
    def make(self):
        i = self.get_inputs()
        reg = sb.FlipFlop(d=i.d, clk=i.clk, l=i.l, r=i.r)
        inverter = OR(a=i.e, bubbles=['y'])
        self.set_tristate(qt=inverter.y)
        self.set_outputs(q=reg.q, qt=reg.q)

        
class ControlUnit(BaseCircuit):
    """
    
    """
    input_labels = 'd clk r'.split()
    output_labels = 'lo lb eu su ea la ei li ce lm ep cp'.split()
    sizes = dict(d=4)
    sizes.update({label : 1 for label in output_labels + ['clk', 'r']})
    def make(self):
        i = self.get_inputs()
        instruction_encode_rom = cb.ROM(2, addr=i.d, ce=Bus.vdd())
        instruction_encode_rom.fburn('instructions_encode.txt')

        counter = sb.Counter(clk=i.clk, size=3)
        eq_comp = cb.EqualityComparator(a=Bus(3, 5), b=counter.q)
        reset_or = OR(a=i.r, b=eq_comp.eq)
        counter.connect(r=reset_or.y)

        control_rom_bus = instruction_encode_rom.q + counter.q
        control_rom = cb.ROM(12, addr=control_rom_bus, ce=Bus.vdd())
        control_rom.fburn('control-rom.txt')

        self.set_outputs(**{label : bus for label, bus in zip(self.output_labels, control_rom.q)})
        

