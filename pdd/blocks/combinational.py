"""
Combinal Logic building blocks
"""
from core import Signal
from dl import BaseCircuit

class Gate(BaseCircuit):
    """
    Implementation of a logic gate. Gate should not be used as a template
    to implement other logic blocks, it is an edge case because it is THE
    fundamental building block.
    """
    input_labels = 'a b'.split()
    output_labels = ['y']
    AND = Signal.AND
    OR = Signal.OR
    XOR = Signal.XOR
    gate_type = {Signal.OR : 'OR', Signal.AND : 'AND', Signal.XOR : 'XOR'}
    def __init__(self, op, **kwargs):
        self.op = op
        super().__init__(**kwargs)

    def update(self):
        self.terminals['a'].propagate()
        self.terminals['b'].propagate()
        i = self.get_inputs()
        out = self.op(i.a.signal, i.b.signal)
        self.terminals['y'].a.signal = out
        self.terminals['y'].propagate() 

    def __repr__(self):
        i = ['{}={}; '.format(label, str(self.terminals[label].a.signal)) for label in self.input_labels]
        o = ['{}={}; '.format(label, str(self.terminals[label].y.signal)) for label in self.output_labels]
        s = 'Gate {}: ' + ''.join(i) + ''.join(o)
        return s.format(self.gate_type[self.op])

class nGate(BaseCircuit):
    """
    n inputs logical gates
    """
    def __init__(self, inputs, op, **kwargs):
        self.input_labels = ['a{}'.format(i) for i in range(inputs)]
        self.output_labels = ['y']
        self.inputs = inputs
        self.op = op
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        gates = [Gate(self.op, size=len(i.a0)) for _ in range(self.inputs - 1)]
        gates[0].connect(a=i.a0, b=i.a1)
        for j, gate in enumerate(gates[1:]):
            gate.connect(a=gates[j].y, b=i[j+2])
        self.set_outputs(y=gates[-1].y)
        
    def __repr__(self):
        i = ['{}={}; '.format(label, str(self.terminals[label].a.signal)) for label in self.input_labels]
        o = ['{}={}; '.format(label, str(self.terminals[label].y.signal)) for label in self.output_labels]
        s = 'Gate {}: ' + ''.join(i) + ''.join(o)
        return s.format(Gate.gate_type[self.op])


def AND(inputs=2, **kwargs):
    """Factory for Logic AND gate"""
    if inputs == 2:
        return Gate(op=Gate.AND, **kwargs)
    elif inputs > 2:
        return nGate(inputs, op=Gate.AND, **kwargs)

def XOR(inputs=2, **kwargs):
    """Factory for Logic XOR gate"""
    if inputs == 2:
        return Gate(op=Gate.XOR, **kwargs)
    elif inputs > 2:
        return nGate(inputs, op=Gate.XOR, **kwargs)

def OR(inputs=2, **kwargs):
    """Factory for Logic OR gate"""
    if inputs == 2:
        return Gate(op=Gate.OR, **kwargs)
    elif inputs > 2:
        return nGate(inputs, op=Gate.OR, **kwargs)


class SimpleMux(BaseCircuit):
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
        self.sizes = {'s' : 1}
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        #Eqt for d0_and = d0~s
        branched_s = i.s.branch(len(i.d0))
        d0_and = AND(a=i.d0, b=branched_s, bubbles=['b'])
        #Eqt for d0_and = d1s
        d1_and = AND(a=i.d1, b=branched_s)
        select_or = OR(a=d0_and.y, b=d1_and.y)
        self.set_outputs(y=select_or.y)


class SimpleDecoder(BaseCircuit):
    """
    Simple 2 input, 4 output decoder
    """
    input_labels = 'a0 a1'.split()
    output_labels = 'y0 y1 y2 y3'.split()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        and0 = AND(a=i.a0, b=i.a1, bubbles='a b'.split())
        and1 = AND(a=i.a0, b=i.a1, bubbles=['b'])
        and2 = AND(a=i.a0, b=i.a1, bubbles=['a'])
        and3 = AND(a=i.a0, b=i.a1)
        self.set_outputs(y0=and0.y, y1=and1.y, y2=and2.y, y3=and3.y)


class Mutiplexer(BaseCircuit):
    """
    Multiplexer circuit with n select lines
    """
    def __init__(self, select_len, **kwargs):
        self.input_labels = ['d{}'.format(i) for i in range(select_len**2)] + ['s']
        self.output_labels = ['y']
        if not select_len > 1:
            raise ValueError("select_len must be > 1")
        self.sizes = {'s': select_len}
        self.select_len = select_len
        super().__init__(**kwargs)

    def make(self):
        #this be confuse, I thought it would be much simpler
        #Harris pg 85 for diagream on hierarchical n-select multiplexer implementation
        i = self.get_inputs()

        #initialize multiplexers
        #formula gives number of multiplexers at any given lvl
        muxes_by_lvl = lambda lvl: int((2**self.select_len)/(2*(lvl+1)))
        gen_muxes = lambda n : [Multiplexer(d0=i.d0) for _ in range(n)]
        levels = [gen_muxes(muxes_by_lvl(i)) for i in range(self.select_len)]
        #connect muxes at lvl 0
        #i is a namedtuple and by input_labels order select line is the last element in the tuple
        #so it gets skipped
        data_lines = [(even, odd) for even, odd in zip(i[:-1:2], i[1:-1:2])] 
        for mux, pair in zip(levels[0], data_lines):
            mux.connect(d0=pair[0], d1=pair[1], s=i.s[0])
        #connect rest of the lvls
        for i in range(1, self.select_len):
            data_lines = [(even.y, odd.y) for even, odd in zip(levels[i-1][::2], levels[i-1][1::2])]
            for mux, pair in zip(levels[i], data_lines):
                mux.connect(d0=pair[0], d1=pair[1])
        #get output from last mux and sets to circuit output
        self.set_outputs(y=levels[-1][0].y)
