"""
Combinal Logic building blocks
"""
from core import Signal
from dl import BaseCircuit, Bus

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
        self.update()

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


class Mux(BaseCircuit):
    """
    Multiplexer circuit with 2 select lines
    """
    input_labels = 'd0 d1 d2 d3 s'.split()
    output_labels = ['y']
    sizes = dict(s=2)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make(self):
        #this be confuse, I thought it would be much simpler
        #Harris pg 85 for diagream on hierarchical n-select multiplexer implementation
        i = self.get_inputs()
        mux_1 = SimpleMux(d0=i.d0, d1=i.d1, s=i.s[0])
        mux_2 = SimpleMux(d0=i.d2, d1=i.d3, s=i.s[0])
        mux_3 = SimpleMux(d0=mux_1.y, d1=mux_2.y, s=i.s[1])
        self.set_outputs(y=mux_3.y)

class HalfAdder(BaseCircuit):
    """
    
    """
    input_labels = 'a b'.split()
    output_labels = 's cout'.split()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        sum = XOR(a=i.a, b=i.b)
        carry = AND(a=i.a, b=i.b)
        self.set_outputs(s=sum.y, cout=carry.y)
        
class FullAdder(BaseCircuit):
    """
    Does not work for TRUE multibit addtion, meaning
    it will execute the operations on a bit by bit basis not on the word
    """
    input_labels = "a b cin".split()
    output_labels = "s cout".split()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        sum = XOR(inputs=3, a0=i.a, a1=i.b, a2=i.cin)

        and0 = AND(a=i.a, b=i.b)
        and1 = AND(a=i.a, b=i.cin)
        and2 = AND(a=i.b, b=i.cin)
        carry = OR(inputs=3, a0=and0.y, a1=and1.y, a2=and2.y)
        self.set_outputs(s=sum.y, cout=carry.y)

class CPA(BaseCircuit):
    """
    
    """
    input_labels = "a b cin".split()
    output_labels = "s cout".split()
    sizes = dict(cin=1, cout=1)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        word_size = self.sizes['a']
        adders = [FullAdder(size=1) for _ in range(word_size)]
        a_split = i.a.split()
        b_split = i.b.split()
        #set input for adders
        for a, b, adder in zip(a_split, b_split, adders):
            adder.connect(a=a, b=b)
        #set cins
        adders[0].connect(cin=i.cin)
        for i, adder in enumerate(adders[1:]):
            adder.connect(cin=adders[i].cout)
        s = Bus.merge([adder.s for adder in adders])
        self.set_outputs(s=s, cout=adders[-1].cout)

class Subtractor(BaseCircuit):
    """
    
    """
    input_labels = "a b".split()
    output_labels = "s".split()
    sizes = dict(cout=1)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        cpa = CPA(a=i.a, b=i.b, cin=Bus.vdd(), bubbles=['b'])
        self.set_outputs(s=cpa.s)
 

class EqualityComparator(BaseCircuit):
    """
    
    """
    input_labels = "a b".split()
    output_labels = "eq".split()
    sizes = dict(eq=1)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        compare = XOR(a=i.a, b=i.b, bubbles=['y'])
        buses = compare.y.split()
        ender = AND(inputs=len(buses))
        ender.connect_sequence(buses)
        self.set_outputs(eq=ender.y)

        
class Comparator(BaseCircuit):
    """
    
    """
    input_labels = 'a b'.split()
    output_labels = 'neq eq lte gt gte lt'.split()
    sizes = {label:1 for label in output_labels}
    bubbles = {label : True for label in 'neq lte gte'.split()}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        eq = EqualityComparator(a=i.a, b=i.b)
        neq = EqualityComparator(a=i.a, b=i.b, bubbles=['eq'])
        lt = Subtractor(a=i.a, b=i.b) # MSB of A-B 1 if A < B
        gte = Subtractor(a=i.a, b=i.b, bubbles=['s']) # MSB of A-B 0 if A < B, so we bubble it
        gt = Subtractor(a=i.b, b=i.a) #MSB of B-A 1 if B < A
        lte = Subtractor(a=i.b, b=i.a, bubbles=['s']) #MSB of B-A 0 if B >= A, so we bubble it
        self.set_outputs(eq=eq.eq, neq=neq.eq,
                         lt=lt.s[-1], gte=gte.s[-1],
                         gt=gt.s[-1], lte=lte.s[-1])



class BaseDecoder(BaseCircuit):
    """
    
    """
    input_labels = "a e".split()
    output_labels = "y0 y1".split()
    sizes = dict(e=1)

    def make(self):
        i = self.get_inputs()
        e_bus = i.e.branch(len(i.a))
        y0_out = AND(a=i.a, b=e_bus, bubbles=['a'])
        y1_out = AND(a=i.a, b=e_bus)
        self.set_outputs(y0=y0_out.y, y1=y1_out.y)
        
class Decoder(BaseCircuit):
    """
    Makes use of recursion to implement n-input decoder with a single
    input port.
    """
    input_labels = 'a e'.split()
    def __init__(self, **kwargs):
        self.sizes = dict(e=1)
        if 'a' in kwargs:
            y_size = 2**len(kwargs['a'])
        elif 'size' in kwargs:
            y_size = 2**kwargs['size']
        else: y_size = 2
        self.output_labels = ['y'+str(i) for i in range(y_size)]
        self.sizes.update({label:1 for label in self.output_labels})
        super().__init__(**kwargs)

    @property
    def y(self):
        return Bus.merge(self.get_buses(self.output_labels))

    def make(self):
        """Recursive implementation inspired by implementation at
        https://www.tutorialspoint.com/digital_circuits/digital_circuits_decoders.htm"""
        i = self.get_inputs()
        if self.sizes['a'] == 1:
            dec = BaseDecoder(a=i.a, e=i.e)
            self.set_outputs(y0=dec.y0, y1=dec.y1)
        else:
            enable_gate = AND(a=i.a, b=i.e.branch(len(i.a)))
            dec1 = Decoder(a=enable_gate.y[:-1], e=enable_gate.y[-1], bubbles=['e'])
            dec2 = Decoder(a=enable_gate.y[:-1], e=enable_gate.y[-1])
            y_buses = {'y'+str(i) : bus for i, bus in enumerate(dec2.y + dec1.y)}
            self.set_outputs(**y_buses)

