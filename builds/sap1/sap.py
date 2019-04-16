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
        select_b = cb.SimpleMux(d0=i.b, d1=i.b, s=i.sub, bubbles=['d1'])
        adder = cb.CPA(a=i.a, b=select_b.y, cin=i.sub)
        self.set_tristate(s=i.e)
        self.set_outputs(s=adder.s)


class RingCounter(BaseCircuit):
    #emotional value only
    input_labels = "clk".split()
    output_labels = "t0 t1 t2 t3 t4 t5".split()
    sizes = dict(clk=1, t0=1, t1=1, t2=1, t3=1, t4=1, t5=1)

    def make(self):
        i = self.get_inputs()
        counter = SettableCounter(d=Bus(3, 1), clk=i.clk)
        adder = cb.CPA(a=Bus(3, 1), b=counter.q)
        dec = cb.Decoder(a=adder.s, e=Bus.vdd())
        counter.connect(l=dec.y7)
        self.set_outputs(t0=dec.y2, t1=dec.y3, t2=dec.y4, t3=dec.y5, t4=dec.y6, t5=dec.y7)

class DoubleELFlipFlop(BaseCircuit):
    """
    
    """
    input_labels = "d e l clk".split()
    output_labels = "q qt".split()
    sizes = dict(e=1, l=1, clk=1)
    def make(self):
        i = self.get_inputs()
        reg = sb.ELFlipFlop(d=i.d, clk=i.clk, e=Bus.vdd(), l=i.l)
        self.set_tristate(qt=i.e)
        self.set_outputs(q=reg.q, qt=reg.q)

        
class ControlUnit(BaseCircuit):
    """
    
    """
    input_labels = 'd clk'.split()
    output_labels = 'cp ep lm ce li ei la ea su eu lb lo'.split()
    sizes = dict(d=4)
    sizes.update({label : 1 for label in output_labels + ['clk']})
    def make(self):
        i = self.get_inputs()
        instruction_encode_rom = sb.ROM(2, addr=i.d, ce=Bus.vdd())
        instruction_encode_rom.fburn('instructions_encode.txt')

        counter = sb.Counter(clk=i.clk, size=3, bubbles=['clk'])
        eq_comp = cb.EqualityComparator(a=Bus(3, 5), b=counter.q)
        counter.connect(reset=eq_comp.eq)

        control_rom_bus = instruction_encode_rom.q + counter.q
        control_rom = sb.ROM(12, addr=control_rom_bus, ce=Bus.vdd())
        control_rom.fburn('control-rom.txt')

        self.set_outputs(**{label : bus for label, bus in zip(self.output_labels, control_rom.q)})
        

#assemble
W = Bus(8)
clk = Bus()
cu = ControlUnit(size=4, clk=clk)

pc = sb.Counter(clk=cu.cp, q=W[:4]) #increment flag
pc.set_tristate(q=cu.ep) #enable flag

acc = DoubleELFlipFlop(d=W, qt=W, clk=clk, e=cu.ea, l=cu.la)
b_reg = sb.ELFlipFlop(d=W, clk=clk, e=Bus.vdd(), l=cu.lb)

alu = ALU(a=acc.q, b=b_reg.q, sub=cu.su, e=cu.eu)

out_reg = sb.ELFlipFlop(d=W, clk=clk, e=Bus.vdd(), l=cu.lo) #set l

mar = sb.ELFlipFlop(d=W[:4], e=Bus.vdd(), clk=clk, l=cu.lm) #set l (very optional)

memory = sb.ROM(8, addr=mar.q, q=W, ce=cu.ce) #set en flag

ir = DoubleELFlipFlop(d=W, qt=W, clk=clk, l=cu.li, e=cu.ei) #set e l flags

cu.connect(d=ir.q[4:])
