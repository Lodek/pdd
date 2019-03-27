import warnings
import blocks.combinational as cb
import blocks.sequential as sb
from blocks.combinational import AND, OR, XOR

__all__ = 'cb sb AND OR XOR'.split()
warnings.warn('Use dir(cb) and dir(sb) to check available blocks')
