import base_tester
from tools import TruthTable

OR = TruthTable([dict(a=0, b=0, y=0),
                 dict(a=0, b=1, y=1),
                 dict(a=1, b=0, y=1),
                 dict(a=1, b=1, y=1)])

AND = TruthTable([dict(a=0, b=0, y=0),
                  dict(a=1, b=0, y=0),
                  dict(a=0, b=1, y=0),
                  dict(a=1, b=1, y=1)])

XOR = TruthTable([dict(a=0, b=0, y=0),
                  dict(a=0, b=1, y=1),
                  dict(a=1, b=0, y=1),
                  dict(a=1, b=1, y=0)])

NOR = TruthTable([dict(a=0, b=0, y=1),
                  dict(a=0, b=1, y=0),
                  dict(a=1, b=0, y=0),
                  dict(a=1, b=1, y=0)])

NAND = TruthTable([dict(a=0, b=0, y=1),
                   dict(a=0, b=1, y=1),
                   dict(a=1, b=0, y=1),
                   dict(a=1, b=1, y=0)])

XNOR = TruthTable([dict(a=0, b=0, y=1),
                   dict(a=0, b=1, y=0),
                   dict(a=1, b=0, y=0),
                   dict(a=1, b=1, y=1)])

BaseMux = TruthTable([dict(s=0, d1=0, d0=0, y=0),
                        dict(s=0, d1=0, d0=1, y=1),
                        dict(s=0, d1=1, d0=0, y=0),
                        dict(s=0, d1=1, d0=1, y=1),
                        dict(s=1, d1=0, d0=0, y=0),
                        dict(s=1, d1=0, d0=1, y=0),
                        dict(s=1, d1=1, d0=0, y=1),
                        dict(s=1, d1=1, d0=1, y=1)])

                       
HalfAdder = TruthTable([dict(a=0, b=0, cout=0, s=0),
                        dict(a=0, b=1, cout=0, s=1),
                        dict(a=1, b=0, cout=0, s=1),
                        dict(a=1, b=1, cout=1, s=0)])

FullAdder = TruthTable([dict(cin=0, a=0, b=0, cout=0, s=0),
                        dict(cin=0, a=0, b=1, cout=0, s=1),
                        dict(cin=0, a=1, b=0, cout=0, s=1),
                        dict(cin=0, a=1, b=1, cout=1, s=0),
                        dict(cin=1, a=0, b=0, cout=0, s=1),
                        dict(cin=1, a=0, b=1, cout=1, s=0),
                        dict(cin=1, a=1, b=0, cout=1, s=0),
                        dict(cin=1, a=1, b=1, cout=1, s=1)])

AND_3in = TruthTable([dict(a2=0, a1=0, a0=0, y=0),
                      dict(a2=0, a1=0, a0=1, y=0),
                      dict(a2=0, a1=1, a0=0, y=0),
                      dict(a2=0, a1=1, a0=1, y=0),
                      dict(a2=1, a1=0, a0=0, y=0),
                      dict(a2=1, a1=0, a0=1, y=0),
                      dict(a2=1, a1=1, a0=0, y=0),
                      dict(a2=1, a1=1, a0=1, y=1)])

BaseDecoder = TruthTable([dict(a=0, e=0, y0=0, y1=0),
                          dict(a=0, e=1, y0=1, y1=0),
                          dict(a=1, e=0, y0=0, y1=0),
                          dict(a=1, e=1, y0=0, y1=1)])

Decoder_1 = TruthTable([dict(a0=0, e=0, y0=0, y1=0),
                        dict(a0=0, e=1, y0=1, y1=0),
                        dict(a0=1, e=0, y0=0, y1=0),
                        dict(a0=1, e=1, y0=0, y1=1)])
