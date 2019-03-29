from dl import Bus

def gen_output_table(circuit): 
    """Return dictionary where keys are output labels and values are lists of
    signals for the given output bus based on the input (given by the index of 
    the list).
    Sequentially assign all possible values to input bus (given by 2 ** (num of inputs)),
    and record the current signal for each output"""
    state = circuit.auto_update
    circuit.auto_update = True
    super_bus = Bus.merge(circuit.get_buses(circuit.input_labels))
    generated_table = []
    for signal in super_bus.sweep():
        super_bus.signal = signal
        generated_table.append(circuit.state_int)

    circuit.auto_update = state
    return generated_table

def gen_pretty_output_table(circuit, input_order=[]):
    """Return dictionary where keys are output labels and values are lists of
    signals for the given output bus based on the input (given by the index of 
    the list).
    Sequentially assign all possible values to input bus (given by 2 ** (num of inputs)),
    and record the current signal for each output"""
    if not input_order:
        input_order = circuit.input_labels
    super_bus = Bus.merge(circuit.get_buses(input_order))
    output_buses = {label: circuit.get_bus(label) for label in circuit.output_labels}
    generated_table = {label : [] for label in circuit.output_labels}
    for signal in super_bus.sweep():
        super_bus.signal = signal
        for label, bus in output_buses.items():
            generated_table[label].append(circuit.terminals_state())
    return generated_table


class TruthTable:
    """
    Abstraction of a truth table. Receive list of inputs and outputs (string for labels),
    and a list of dictionary. Each dict is a row in the truth table.
    eg [dict(a=0, b=0, y=0), dict(a=0, b=1, y=1)]. Assume dict sweeps out
    all possible values for the inputs.
    """
    def __init__(self, inputs, outputs, dicts):
        self.inputs = sorted(inputs)
        self.outputs = sorted(outputs)
        if len(dicts) != 2 ** len(inputs):
            raise ValueError('dict of index {} has missing values'.format(i))
        self.dicts = dicts
        self.table = []
        self.listify_dicts()

    def listify_dicts(self):
        """Transform the list of state dicts into a list of lists.
        Each output will have its own list and the order of the values
        are given by the get_index function."""
        for output in self.outputs:
            self.table.append([0] * 2**len(self.inputs))

        index_lookup = {label : i for i, label in enumerate(self.outputs)}
        for d in self.dicts:
            i = self.get_index(d)
            for label, index in index_lookup.items():
                self.table[index][i] = d[label]

    def get_index(self, dict):
        """Given a dictionary representing the state, return an
        integer which is the index of that state in the list of
        outputs. Bitshifts values as to form a number which matches
        the combination of inputs"""
        bit_rep = {label : i for i, label in enumerate(self.inputs)}
        index = 0
        for label, i in bit_rep.items():
            index = index | dict[label] << i
        return index

    def __eq__(self, other):
        """Two TruthTables are equal if their input labels,
        output labels and table are equal"""
        if not self.inputs == other.inputs:
            return False
        if not self.outputs == other.outputs:
            return False
        if not self.table == other.table:
            return False
        return True

        
