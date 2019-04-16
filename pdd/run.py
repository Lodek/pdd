"""Use on ipython to remove repitition of testing stuff"""

from blocks import *
from dl import Bus
from core import Wire
from tools import *
import logging
import sap

logging.basicConfig(filename=__file__+'.log', filemode='w', level=logging.DEBUG)

u = Wire.updater
Wire.auto_update = True

cu = sap.ControlUnit(size=4)

cu.d = 0x0
gen = SignalGen.pulse(cu.clk, 10)
signals = [cu.state for _ in gen.iterate()]

