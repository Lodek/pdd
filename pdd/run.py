"""Use on ipython to remove repitition of testing stuff"""

from gates import *
import blocks
from dl import Bus
from core import Wire

u = Wire.updater
Wire.auto_update = True

def get_mux(n=1):
    return blocks.Multiplexer(size=n)