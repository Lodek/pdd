"""Use on ipython to remove repitition of testing stuff"""

from blocks import *
from dl import Bus
from core import Wire
from tools import *
import logging

logging.basicConfig(filename='run.log', filemode='w', level=logging.DEBUG)

u = Wire.updater
Wire.auto_update = True

#cpa = cb.CPA(size=4)
#sub = cb.Subtractor(size=4)
#eq = cb.EqualityComparator(size=4)

g = AND(inputs=3)


