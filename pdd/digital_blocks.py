from core import *

class HalfAdder(Circuit):

    def __init__(self, a, b, s=None, cout=None):
        inputs_bus = {'a': a, 'b' : b}
        outputs_bus = {'s' : s, 'cout' : cout}
        super().__init__(inputs_bus, outputs_bus)

    def _func_spec(self):
        self.s_gate = Gate((self.terminals['in']['a'].out_bus,
                       self.terminals['in']['b'].out_bus), 'or')
        self.cout_gate = Gate((self.terminals['in']['a'].out_bus,
                          self.terminals['in']['b'].out_bus), 'and')
        self.terminals['out']['s'].in_bus = s_gate.output
        self.terminals['out']['cout'].in_bus = cout_gate.output

    def compute(self):
        for terminal in self.terminals['in'].items():
            terminal.propagate()
        self.s_gate.compute()
        self.cout_gate.compute()
        for terminal in self.terminals['out'].items():
            terminal.propagate()
        
a = Bus('000')
b = Bus('101')
adder = HalfAdder(a, b)
cout_bus = adder.outputs['cout']
s_bus = adder.outputs['s']
adder.compute()

        
