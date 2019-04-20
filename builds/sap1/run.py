from pdd.tools import SignalGen
import sap

proc = sap.Sap1Processor()
gen = SignalGen.pulse(proc.clk, 30)
proc.r.set()
proc.clk.pulse()
proc.r.reset()

states = [proc.state for _ in gen.iterate()]


