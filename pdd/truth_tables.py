from tools import TruthTable

OR = TruthTable('a b'.split(), ['y'],
                [dict(a=0, b=0, y=0),
                 dict(a=0, b=1, y=1),
                 dict(a=1, b=0, y=1),
                 dict(a=1, b=1, y=1)])

AND = TruthTable('a b'.split(), ['y'],
                 [dict(a=0, b=0, y=0),
                  dict(a=1, b=0, y=0),
                  dict(a=0, b=1, y=0),
                  dict(a=1, b=1, y=1)])

XOR = TruthTable('a b'.split(), ['y'],
                 [dict(a=0, b=0, y=0),
                  dict(a=0, b=1, y=1),
                  dict(a=1, b=0, y=1),
                  dict(a=1, b=1, y=0)])

NOR = TruthTable('a b'.split(), ['y'],
                 [dict(a=0, b=0, y=1),
                  dict(a=0, b=1, y=0),
                  dict(a=1, b=0, y=0),
                  dict(a=1, b=1, y=0)])

NAND = TruthTable('a b'.split(), ['y'],
                  [dict(a=0, b=0, y=1),
                   dict(a=0, b=1, y=1),
                   dict(a=1, b=0, y=1),
                   dict(a=1, b=1, y=0)])

XNOR = TruthTable('a b'.split(), ['y'],
                  [dict(a=0, b=0, y=1),
                   dict(a=0, b=1, y=0),
                   dict(a=1, b=0, y=0),
                   dict(a=1, b=1, y=1)])

SimpleMux = TruthTable('s d0 d1'.split(), ['y'],
                       [dict(s=0, d1=0, d0=0, y=0),
                        dict(s=0, d1=0, d0=1, y=1),
                        dict(s=0, d1=1, d0=0, y=0),
                        dict(s=0, d1=1, d0=1, y=1),
                        dict(s=1, d1=0, d0=0, y=0),
                        dict(s=1, d1=0, d0=1, y=0),
                        dict(s=1, d1=1, d0=0, y=1),
                        dict(s=1, d1=1, d0=1, y=1)])

SimpleDecoder = TruthTable('a1 a0'.split(), 'y3 y2 y1 y0'.split(),
                       [dict(a1=0, a0=0, y3=0, y2=0, y1=0, y0=1),
                        dict(a1=0, a0=1, y3=0, y2=0, y1=1, y0=0),
                        dict(a1=1, a0=0, y3=0, y2=1, y1=0, y0=0),
                        dict(a1=1, a0=1, y3=1, y2=0, y1=0, y0=0)])
                        

HalfAdder = TruthTable('a b'.split(), 'cout s'.split(),
                       [dict(a=0, b=0, cout=0, s=0),
                        dict(a=0, b=1, cout=0, s=1),
                        dict(a=1, b=0, cout=0, s=1),
                        dict(a=1, b=1, cout=1, s=0)])

FullAdder = TruthTable('a b cin'.split(), 'cout s'.split(),
                       [dict(cin=0, a=0, b=0, cout=0, s=0),
                        dict(cin=0, a=0, b=1, cout=0, s=1),
                        dict(cin=0, a=1, b=0, cout=0, s=1),
                        dict(cin=0, a=1, b=1, cout=1, s=0),
                        dict(cin=1, a=0, b=0, cout=0, s=1),
                        dict(cin=1, a=0, b=1, cout=1, s=0),
                        dict(cin=1, a=1, b=0, cout=1, s=0),
                        dict(cin=1, a=1, b=1, cout=1, s=1)])

AND_3in = TruthTable('a0 a1 a2'.split(), ['y'],
                     [dict(a2=0, a1=0, a0=0, y=0),
                      dict(a2=0, a1=0, a0=1, y=0),
                      dict(a2=0, a1=1, a0=0, y=0),
                      dict(a2=0, a1=1, a0=1, y=0),
                      dict(a2=1, a1=0, a0=0, y=0),
                      dict(a2=1, a1=0, a0=1, y=0),
                      dict(a2=1, a1=1, a0=0, y=0),
                      dict(a2=1, a1=1, a0=1, y=1)])

BaseDecoder = TruthTable('a e'.split(), 'y0 y1'.split(),
                         [dict(a=0, e=0, y0=0, y1=0),
                          dict(a=0, e=1, y0=1, y1=0),
                          dict(a=1, e=0, y0=0, y1=0),
                          dict(a=1, e=1, y0=0, y1=1)])

Decoder_1 = TruthTable('a0 e'.split(), 'y0 y1'.split(),
                       [dict(a0=0, e=0, y0=0, y1=0),
                        dict(a0=0, e=1, y0=1, y1=0),
                        dict(a0=1, e=0, y0=0, y1=0),
                        dict(a0=1, e=1, y0=0, y1=1)])
