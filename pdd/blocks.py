
class Adder(BaseCircuit):

    def __init__(self, **kwargs):
        self.input_labels = 'a b en'.split()
        self.ouput_labels = ['y']
        self.bus_sizes = dict(something=1)
        super().__init__()

    def wiring(self):
        i = self.get_inputs()
        g1 = AND(a=i.a, b=i.b)
        self.set_tris(y=i.en)
        self.set_outputs(y=g1.output())
