from blocks import *
import pdd.sequential_blocks as sb
import pdd.combinational_blocks as cb
from pdd.dl import Bus, BaseCircuit

class Sap1Processor(BaseCircuit):
    """
    Implementation of the SAP-1 processor
    """
    input_labels = "clk r".split()
    output_labels = "out w".split()
    sizes = dict(clk=1, r=1, out=8, w=8)

    def make(self):
        i = self.get_inputs()
        W = i.w
        clk = i.clk
        
        cu = ControlUnit(size=4, r=i.r, clk=i.clk)

        pc = sb.Counter(clk=cu.cp, q=W[:4], r=i.r) #counter size 4, 4 LSB of W
        pc.set_tristate(q=cu.ep) #enable flag

        acc = DoubleFlipFlop(d=W, qt=W, clk=clk, e=cu.ea, l=cu.la, r=i.r)
        b_reg = sb.FlipFlop(d=W, clk=clk, l=cu.lb, r=i.r) #no output tristate

        alu = ALU(a=acc.q, b=b_reg.q, sub=cu.su, e=cu.eu)

        out_reg = sb.FlipFlop(d=W, clk=clk, l=cu.lo, r=i.r) #no output tristate as well
        self.set_outputs(out=out_reg.q)

        mar = sb.FlipFlop(d=W[:4], clk=clk, l=cu.lm, r=i.r) #mar has no otuput tristate either

        memory = cb.ROM(8, addr=mar.q, q=W, ce=cu.ce) #set en flag
        memory.fburn('program_rom.txt')

        ir = DoubleFlipFlop(d=W, qt=W, clk=clk, l=cu.li, e=cu.ei, r=i.r) #set e l flags

        cu.connect(d=ir.q[4:])

