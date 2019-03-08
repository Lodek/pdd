from core import *

class HalfAdderA(Circuit):

    def __init__(self, a, b, s=None, cout=None):
        inputs_bus = {'a': a, 'b' : b}
        outputs_bus = {'s' : s, 'cout' : cout}
        super().__init__(inputs_bus, outputs_bus)

    def _func_spec(self):
        nodes = self.nodes
        self.circuits['s'] = Gate([nodes('in', 'a'), nodes('in', 'b')], 'or')
        self.circuits['cout'] = Gate((nodes('in', 'a'), nodes('in', 'b')), 'and')
        self.set_nodes('out', 's', self.circuits['s'].output)
        self.set_nodes('out', 'cout', self.circuits['cout'].output)


class HalfAdderB(Circuit):

    def __init__(self, inverted=[]):
        self.inverted = inverted
        super().__init__('a b'.split(), 's cout'.split())
        
    def _func_spec(self):
        nodes = self.nodes
        s_g = Gate('or')
        cout_g = Gate('and')
        s_g.connect({'a':nodes['a'], 'b':nodes['b']})
        cout_g.connect({'a':nodes['a'], 'b':nodes['b']})
        
        self.set_nodes('s', s_g.output)
        self.set_nodes('cout', cout_g.output)

        self.circuits = [s_g, cout_g]
        
a = Bus('000')
b = Bus('101')
adder = HalfAdder(a, b)
adder.compute()
print(adder.outputs['cout'])
print(adder.outputs['s'])

        
