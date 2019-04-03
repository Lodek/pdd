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

dec = cb.Decoder(size=3)
dec.e.set()
states = gen_output_table(dec, ['a'])
