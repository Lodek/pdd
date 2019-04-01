class Multiplexer(BaseCircuit):
    """
    Multiplexer circuit with n select lines
    """
    output_labels = ['y']
    def __init__(self, select_len, **kwargs):
        self.input_labels = ['d{}'.format(i) for i in range(select_len**2)] + ['s']
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
        gen_muxes = lambda n : [SimpleMux(d0=i.d0) for _ in range(n)]
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

