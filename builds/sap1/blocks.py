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
        mux = cb.BaseMux(d0=i.d, s=i.l)
        reg = sb.FlipFlop(d=mux.y, clk=i.clk, r=i.r)
        mux.connect(d1=reg.q)
        inverter = OR(a=i.e, bubbles=['y'])
        self.set_tristate(qt=inverter.y)
        self.set_outputs(q=reg.q, qt=reg.q)

        
class ControlUnit(BaseCircuit):
    """
    
    """
    input_labels = 'd ic'.split()
    output_labels = 'lo lb eu su ea la ei li ce lm ep cp'.split()
    sizes = dict(d=4, ic=3)
    sizes.update({label : 1 for label in output_labels})
    def make(self):
        i = self.get_inputs()
        instruction_encode_rom = cb.ROM(2, addr=i.d, ce=Bus.vdd())
        instruction_encode_rom.fburn('instructions_encode.txt')

        control_rom_bus = instruction_encode_rom.q + i.ic
        control_rom = cb.ROM(12, addr=control_rom_bus, ce=Bus.vdd())
        control_rom.fburn('control-rom.txt')

        self.set_outputs(**{label : bus for label, bus in zip(self.output_labels, control_rom.q)})
        
class StateArchitectureUnit(BaseCircuit):
    """
    
    """
    input_flags = 'lo lb eu su ea la ei li ce lm ep cp'
    input_labels = ('r win clk lwin ' + input_flags).split()
    output_labels = "wout ic out iw".split()
    sizes = dict(win=8, wout=8, out=8, ic=3, iw=4)
    sizes.update({l:1 for l in input_flags.split() + 'r clk lwin'.split()})

    def make(self):
        i = self.get_inputs()
        self.set_outputs(wout=i.win)
        self.set_tristate(win=i.lwin)
        W = i.win
        clk = i.clk
        r = i.r

        pc = sb.Counter(clk=clk, c=i.cp, q=W[:4], r=r) #counter size 4, 4 LSB of W
        pc_i = INV(a=i.ep)
        pc.set_tristate(q=pc_i.y) #enable flag
        self.pc = pc
        acc = DoubleFlipFlop(d=W, qt=W, clk=clk, e=i.ea, l=i.la, r=r)
        self.acc = acc
        b_reg = sb.FlipFlop(d=W, clk=clk, l=i.lb, r=r) #no output tristate
        self.br = b_reg
        alu = ALU(a=acc.q, b=b_reg.q, sub=i.su, e=i.eu, s=W)
        self.alu = alu
        out_reg = sb.FlipFlop(d=W, clk=clk, l=i.lo, r=r) #no output tristate as well
        self.out_reg = out_reg
        self.set_outputs(out=out_reg.q)
        mar = sb.FlipFlop(d=W[:4], clk=clk, l=i.lm, r=r) #mar has no otuput tristate either
        self.mar = mar
        rom = cb.ROM(8, addr=mar.q, q=W, ce=i.ce) #set en flag
        self.rom = rom
        ir = DoubleFlipFlop(d=W, qt=W, clk=clk, l=i.li, e=i.ei, r=r) #set e l flags
        self.ir = ir
        self.set_outputs(iw=ir.q[4:])
        mic = sb.Counter(clk=clk, size=3, bubbles=['clk'])
        mic.c.set()
        self.mic = mic
        self.set_outputs(ic=mic.q)
        eq_comp = cb.EqualityComparator(a=Bus(3, 5), b=mic.q)
        reset_or = OR(a=r, b=eq_comp.eq)
        mic.connect(r=reset_or.y)
       
    def load_program(self, f):
        self.rom.fburn(f)

    def reset(self):
        self.r.set()
        self.clk.pulse()
        self.r.reset()

    def init_flags_nop(self):
        sigs = dict(lo=1, lb=1, eu=1, su=0, ea=1, la=1, ei=1, li=1, ce=0, lm=1, ep=1, cp=0)
        for label, value in sigs.items():
            self.get_bus(label).signal = value
      
    def swin(self, s):
        self.lwin = 1
        self.win = s
        self.lwin = 0

class Processor(BaseCircuit):
    """
    Implementation of the SAP-1 processor
    """
    input_labels = "clk r".split()
    output_labels = "out wout".split()
    sizes = dict(clk=1, r=1, lwin=1, out=8, win=8, wout=8)
       
    def make(self):
        i = self.get_inputs()
        clk = i.clk
        r = i.r
        sa = StateArchitectureUnit(wout=i.wout, r=r, clk=clk, out=i.out)
        cu = ControlUnit(ic=sa.ic, d=sa.iw)
        sa.connect(lo=cu.lo, lb=cu.lb, eu=cu.eu, su=cu.su, ea=cu.ea,
                   la=cu.la, ei=cu.ei, li=cu.li, ce=cu.ce, lm=cu.lm,
                   ep=cu.ep, cp=cu.cp)
        self.sa = sa
        self.cu = cu

    def load_rom(self, f):
        self.sa.load_program(f)

    def reset(self):
        self.cu.ic = 1
        self.cu.ic = 0
        self.sa.reset()
        
