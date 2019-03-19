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
 
class Multiplexer(BaseCircuit):
    """
    Basic 2:1 multiplexer. 
    inputs: s, d0, d1
    outputs: y
    d0 when s=0
    d1 when s=1
    """
    def __init__(self, **kwargs):
        self.input_labels = 's d0 d1'.split()
        self.output_labels = ['y']
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        #Eqt for d0_and = d0~s
        d0_and = AND(a=i.d0, b=i.s, bubbles=['b'])
        #Eqt for d0_and = d1s
        d1_and = AND(a=i.d1, b=i.s)
        select_or = OR(a=d0_and.y, b=d1_and.y)
        self.set_outputs(y=select_or.y)

        
