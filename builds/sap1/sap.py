from pdd.dl import Bus
from pdd.tools import TruthTable, BaseCircuitTester, Inspector
from pdd.tools import SignalGen, Inspector
from blocks import *

p = Processor()
clk = p.clk
p.load_rom('p3.txt')
p.reset()
ins = Inspector(dict(p=p, sa=p.sa))
ins.inspect()
for i in range(6*4+1):
    print(i)
    clk.pulse()
    ins.inspect()

