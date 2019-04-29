from pdd.dl import Bus
from pdd.tools import TruthTable, BaseCircuitTester, Inspector
from pdd.tools import SignalGen, Inspector
from blocks import *

p1 = Processor()
p1.load_rom('p1.txt')
clk = p1.clk
p2 = Processor(clk=clk)
p2.load_rom('p2.txt')
p3 = Processor(clk=clk)
p3.load_rom('p3.txt')
p1.reset()
p2.reset()
p3.reset()
for i in range(6*4+1):
    print("clock " + str(i))
    clk.pulse()

print("resultado prog. 1" + repr(p1))
print("resultado prog. 2" + repr(p2))
print("resultado prog. 3" + repr(p3))
