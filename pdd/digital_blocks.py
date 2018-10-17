from core import *

class HalfAdder(Circuit):

    def __init__(self, a, b, s=None, cout=None):
        inputs_bus = {'a': a, 'b' : b}
        outputs_bus = {'s' : s, 'cout' : cout}
        super().__init__(inputs_bus, outputs_bus)

    def _func_spec(self):
        get_bus = self.get_bus
        self.circuits['s'] = Gate([nodes('in', 'a'), nodes('in', 'b')], 'or')
        self.circuits['cout'] = Gate((nodes('in', 'a'), nodes('in', 'b')), 'and')
        
        set_nodes('out', 's', self.circuits['s'].output)
        set_nodes('out', 'cout', self.circuits['cout'].output)



            
        
a = Bus('000')
b = Bus('101')
adder = HalfAdder(a, b)
cout_bus = adder.outputs['cout']
s_bus = adder.outputs['s']
adder.compute()

        
