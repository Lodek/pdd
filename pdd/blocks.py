from core import Signal
from dl import BaseCircuit

class Gate(BaseCircuit):
    """
    Implementation of a logic gate. Gate should not be used as a template
    to implement other logic blocks, it is an edge case because it is THE
    fundamental building block.
    """
    AND = Signal.AND
    OR = Signal.OR
    XOR = Signal.XOR
    def __init__(self, op, **kwargs):
        self.input_labels = 'a b'.split()
        self.output_labels = ['y']
        self.op = op
        super().__init__(**kwargs)

    def update(self):
        self.terminals['a'].propagate()
        self.terminals['b'].propagate()
        i = self.get_inputs()
        out = self.op(i.a.signal, i.b.signal)
        self.terminals['y'].a.signal = out
        self.terminals['y'].propagate() 
    
   

        
