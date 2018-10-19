from core import *
from blocks import *

class ALU(Circuit):

    def __init__(self, a, b, f, y=None):
        inputs = 'a b f'.split()
        outputs = ['y']
        super().__init__(inputs, outputs)

    def _func_spec(self):

        mux_b = Mux(1, invert=('1'))
        andg = Gate('and')
        org = Gate('or')
        adder = Adder()
        mux_select = Mux(2)

        mux_b.connect({'1':self.node['b'], '0':self.node['b'],
                         's':self.node['f'][2]})
        
        andg.connect(dict('a'=self.node['a'], 'b'=mux_b.output))
        org.connect(dict('a'=self.node['a'], 'b'=mux_b.output))

        adder.connect(dict('a'=self.node['a'], 'b'=mux.output,
                           'cin'=self.node['f'][2]))

        mux_connections = {'0':andg.output, '1':org.output, '2':adder.outputs['s'], '4':GND, 's':self.nodes['f'][:2]}
        mux_select.connect(mux_connections)

        self.circuits = [mux_b, andg, org, adder, mux_select]
        
            
        
