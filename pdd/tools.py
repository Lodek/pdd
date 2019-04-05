from dl import Bus

import re

def gen_output_table(circuit, labels=[]): 
    """Return dictionary where keys are output labels and values are lists of
    signals for the given output bus based on the input (given by the index of 
    the list).
    Sequentially assign all possible values to input bus (given by 2 ** (num of inputs)),
    and record the current signal for each output"""
    state = circuit.auto_update
    circuit.auto_update = True
    if not labels:
        labels = circuit.input_labels
    super_bus = Bus.merge(circuit.get_buses(labels))
    generated_table = []
    for signal in super_bus.sweep():
        super_bus.signal = signal
        generated_table.append(circuit.state_int)

    circuit.auto_update = state
    return generated_table

def sweep(circuit, labels=[]): 
    """Return dictionary where keys are output labels and values are lists of
    signals for the given output bus based on the input (given by the index of 
    the list).
    Sequentially assign all possible values to input bus (given by 2 ** (num of inputs)),
    and record the current signal for each output"""
    state = circuit.auto_update
    circuit.auto_update = True
    if not labels:
        labels = circuit.input_labels
    super_bus = Bus.merge(circuit.get_buses(labels))
    generated_table = []
    for signal in super_bus.sweep():
        super_bus.signal = signal
        generated_table.append(circuit.state)

    circuit.auto_update = state
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

        
class SignalGen:
    """"
    Automated signal assignment to Buses. Dictionary of buses with labels for buses
    are used along with a list of dicts with signals for these buses; eg.
    buses = dict(a=Bus(), b=Bus())
    signals = [dict(a=1, b=0), dict(a=0)]
    That way SignalGen will assign the given signals sequentially at each cycle.
    """
    def __init__(self, buses, signals):
        self.buses = buses
        self.signals = signals
        self.next_q = []
        
    def next(self):
        """Call to next will assign the next dictionary of values to the bus
        sequentially. next is a generator thus it is an iterable.
        Return the dictionary of signals just assigned"""
        if not self.next_q:
            self.next_q = self.signals
        dic = self.next_q.pop(0)
        for label, signal in dic.items():
            self.buses[label].signal = signal
        return dic
             

    def all(self):
        """Applies all signals to the buses sequentially without stopping"""
        for _ in self.n(): pass

    def _clock_pulse(self):
        """change signals and add a clock pulse to each dictionary"""
        pass

class IOHelper:

    @classmethod
    def _remove_comments(cls, txt):
        r_str = r'#.*\n'
        comp = re.compile(r_str)
        clean_text = comp.sub('\n', txt)
        return clean_text

    @classmethod
    def _get_text(cls, p):
        with open(p) as f:
            text = f.read()
        return cls._remove_comments(text)

    @classmethod
    def _caster(cls, s):
        s = s.lower()
        if 'x' in s:
            return int(s, 16)
        elif 'b' in s:
            return int(s, 2)
        else:
            return int(s)
        

    @classmethod
    def parse_signals(cls, p):
        text = cls._get_text(p)

        lines = [line for line in text.split('\n') if line]
        labels = lines[0].split()
        body = [line.split() for line in lines[1:]]
        
        signals = []
        for line in body:
            d = {label : cls._caster(signal) for label, signal in zip(labels, line) if '-' not in signal}
            signals.append(d)
        return signals
        
    @classmethod
    def parse_memory(cls, p):
        text = cls._get_text(p)
        return [cls._caster(line) for line in text.split('\n') if line]
