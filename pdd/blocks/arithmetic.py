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
        a_split = i.a.aplit()
        b_split = i.b.split()
        #set input for adders
        for a, b, adder in zip(a_split, b_split, adders):
            adder.connect(a=a, b=b)
        #set cins
        adders[0].connect(cin=i.cin)
        for i, adder in enumerate(adders[1:]):
            adder.connect(cin=adders[i].cout)
        s = Bus.merge(adder.s for adder in adders)
        self.set_outputs(s=s, cout=adders[-1].cout)

class Subtractor(BaseCircuit):
    """
    
    """
    input_labels = "a b cin".split()
    output_labels = "s cout".split()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        cpa = CPA(a=a, b=b, cin=Bus.vdd(), bubbles=['b'])
        self.set_outputs(cout=cpa.cout, s=cpa.s)
        
            
class EqualityComparator(BaseCircuit):
    """
    
    """
    input_labels = "a b".split()
    output_labels = "eq".split()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def make(self):
        i = self.get_inputs()
        compare = XOR(a=i.a, b=i.b, bubbles=['y'])
        buses = compare.y.split()
        ender = AND(inputs=len(buses))
        ender.connect_seq(buses)

