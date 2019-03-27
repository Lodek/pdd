"""Use on ipython to remove repitition of testing stuff"""

from blocks.gates import *
import blocks.combinational as cb
import blocks.sequential as sb
from dl import Bus
from core import Wire
from tools import *

u = Wire.updater
Wire.auto_update = True

def get_mux(n=1):
    return cb.Multiplexer(size=n)
