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

def AND(**kwargs):
    """Factory for Logic AND gate"""
    return Gate(op=Gate.AND, **kwargs)

def XOR(**kwargs):
    """Factory for Logic XOR gate"""
    return Gate(op=Gate.XOR, **kwargs)

def OR(**kwargs):
    """Factory for Logic OR gate"""
    return Gate(op=Gate.OR, **kwargs)
 
class HalfAdder(BaseCircuit):

    def __init__(self, **kwargs):
        self.input_labels = 'a b'.split()
        self.output_labels = 'cout s'.split()
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        g1 = XOR(a=i.a, b=i.b)
        g2 = AND(a=i.a, b=i.b)
        self.set_outputs(cout=g2.y, s=g1.y)
        
