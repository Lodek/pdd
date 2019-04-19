"""
Combinal Logic building blocks
"""
from pdd.core import Signal
from pdd.dl import BaseCircuit, Bus

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

class BaseMux(BaseCircuit):
    """
    Basic 2:1 multiplexer. 
    inputs: s, d0, d1
    outputs: y
    d0 when s=0
    d1 when s=1
    """
    input_labels = 's d0 d1'.split()
    output_labels = 'y'.split()
    sizes = dict(s=1)

    def make(self):
        i = self.get_inputs()
        #Eqt for d0_and = d0~s
        branched_s = i.s.branch(len(i.d0))
        d0_and = AND(a=i.d0, b=branched_s, bubbles=['b'])
        #Eqt for d0_and = d1s
        d1_and = AND(a=i.d1, b=branched_s)
        select_or = OR(a=d0_and.y, b=d1_and.y)
        self.set_outputs(y=select_or.y)


class Mux(BaseCircuit):
    """
    
    """
    output_labels = 'y'.split()
    def __init__(self, select_len=None, **kwargs):
        if not select_len:
            try:
                select_len = len(kwargs['s'])
            except KeyError:
                raise ValueError('Multiplexer needs select_len or s bus')
        self.input_labels = ['s'] + ['d'+str(i) for i in range(2 ** select_len)]
        self.sizes = dict(s=select_len)
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        mux_by_depth = lambda n : int((2 ** len(i.s)) / (2 * (n + 1)))
        layers = []
        for n, b in enumerate(i.s):
            muxes = [BaseMux(s=b, d0=i.d0) for _ in range(mux_by_depth(n))]
            layers.append(muxes)
        output_previous = [(d0, d1) for d0, d1 in zip(i[1::2], i[2::2])] 
        for muxes  in layers:
            for buses , mux in zip(output_previous, muxes):
                mux.connect(d0=buses[0], d1=buses[1])
            if len(muxes) > 1:
                output_previous = [(d0_mux.y, d1_mux.y) for d0_mux, d1_mux in zip(muxes[::2], muxes[1::2])]
        self.set_outputs(y=layers[-1][0].y)
        
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

    def make(self):
        i = self.get_inputs()
        eq = EqualityComparator(a=i.a, b=i.b)
        neq = EqualityComparator(a=i.a, b=i.b, bubbles=['eq'])
        lt = Subtractor(a=i.a, b=i.b) # MSB of A-B 1 if A < B
        gte = Subtractor(a=i.a, b=i.b, bubbles=['s']) # MSB of A-B 0 if A >= B, so we bubble it
        gt = Subtractor(a=i.b, b=i.a) #MSB of B-A 1 if A > B
        lte = Subtractor(a=i.b, b=i.a, bubbles=['s']) #MSB of B-A 0 if A <= B, so we bubble it
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
            dec1 = Decoder(a=i.a[:-1], e=i.a[-1], bubbles=['e'])
            dec2 = Decoder(a=i.a[:-1], e=i.a[-1])
            enable_gates = [AND(a=bus, b=i.e) for bus in dec2.y + dec1.y]
            y_buses = {'y'+str(i) : gate.y for i, gate in enumerate(enable_gates)}
            self.set_outputs(**y_buses)


class ROM(BaseCircuit):
    """
    Implementation of ROM. Use burn_rom method to assign values to rom.
    Takes the memory word size as a parameter. The number of words in ROM is
    give by the size of the addr bus.
    """
    input_labels = "addr ce".split()
    output_labels = "q".split()
    def __init__(self, word_size, **kwargs):
        self.word_size = word_size
        self.sizes = dict(q=word_size, ce=1)
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        W_bus = i.q
        addr_decoder = Decoder(a=i.addr, e=Bus.vdd())
        self.set_tristate(q=i.ce)
        words = len(addr_decoder.y)
        self.cells = [OR(size=self.word_size) for _ in range(words)]
        for cell, bus in zip(self.cells, addr_decoder.y):
            cell.set_tristate(y=bus)
            cell.connect(y=W_bus)

    def fburn(self, f):
        """Call IOHelper on f to open a file and get the memory contents
        then burn the rom with the words in f"""
        words = tools.IOHelper.parse_memory(f)
        self.burn(words)
        
    def burn(self, contents):
        """Assign word in contents sequentially to memory cells"""
        for word, cell in zip(contents, self.cells):
            cell.a = word

