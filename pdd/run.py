"""Use on ipython to remove repitition of testing stuff"""

from blocks import *
from dl import Bus
from core import Wire
from tools import *
import logging
import harris

#logging.basicConfig(filename=__file__+'.log', filemode='w', level=logging.DEBUG)
u = Wire.updater
Wire.auto_update = True


rom = sb.ROM(8, size=4)
rom.clk.pulse()
