path_to_codebase = '../../pdd'
sys.path.append(path_to_codebase)
from pdd.blocks import *
from pdd.dl import Bus, BaseCircuit

class Sap1Processor(BaseCircuit):
    """
    Implementation of the SAP-1 processor
    """
    input_labels = "clk".split()
    output_labels = "out w".split()
    sizes = dict(clk=1, out=8, w=8)

    def make(self):
        i = self.get_inputs()
        W = i.w
        clk = i.clk

        cu = ControlUnit(size=4, clk=clk)

        pc = sb.Counter(clk=cu.cp, q=W[:4])
        pc.set_tristate(q=cu.ep) #enable flag

        acc = DoubleFlipFlop(d=W, qt=W, clk=clk, e=cu.ea, l=cu.la)
        b_reg = sb.FlipFlop(d=W, clk=clk, l=cu.lb)

        alu = ALU(a=acc.q, b=b_reg.q, sub=cu.su, e=cu.eu)

        out_reg = sb.FlipFlop(d=W, clk=clk, l=cu.lo) #set l
        self.set_outputs(out=out_reg.q)

        mar = sb.FlipFlop(d=W[:4], clk=clk, l=cu.lm) #set l (very optional)

        memory = sb.ROM(8, addr=mar.q, q=W, ce=cu.ce) #set en flag
        memory.fburn('program_rom.txt')

        ir = DoubleELFlipFlop(d=W, qt=W, clk=clk, l=cu.li, e=cu.ei) #set e l flags

        cu.connect(d=ir.q[4:])

