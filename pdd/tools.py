from pdd.dl import Bus
import unittest, re

class TruthTable:
    """
    Simple abstraction for a truthtable. Truth table is modelled as a list of
    dictionaries, each row in the table correspond to a dictionary.
    Equality of the given list ignores order, checks whether each element is
    in the other list. If both lists have the same dicts, the tables are equal.
    """
    def __init__(self, dicts):
       self.dicts = dicts

    def __eq__(self, other):
        if len(self.dicts) != len(other.dicts):
            return False
        for d in self.dicts:
            if d not in other.dicts:
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

    @classmethod
    def sweep_circuit(cls, circuit):
        """From circuit generate a list of signals that sweep over all
        possible value for circuit's input buses, return signalgen object 
        with those values"""
        buses = {label : circuit.get_bus(label) for label in circuit.input_labels}
        return cls.sweep(buses)

    @classmethod
    def sweep(cls, buses):
        """From dict of buses, generate list of signals that sweep over all 
        possible value for buses. Return instance of SignalGen with the list of
        dictionaries as signals"""
        labels = list(buses.keys())
        listed_buses = [buses[label] for label in labels]
        super_bus = Bus.merge(listed_buses)
        #tuple of slices that will enable isolating the signal value for a bus at each time
        #tuple consists of a right bitshift value and a mask to isolate the value of the signal
        #for that particular bus
        bus_slices = [(0, 2**len(listed_buses[0])-1)]
        bus_slices += [(len(Bus.merge(listed_buses[:i+1])), 2**len(bus)-1) for i, bus in enumerate(listed_buses[1:])]

        values = range(2**len(super_bus))
        signals = [] 
        for value in values:
            d = {label: (value >> slice[0]) & (slice[1]) for label, slice in zip(labels, bus_slices)}
            signals.append(d)
        return cls(buses, signals)

    @classmethod
    def pulse(cls, bus, n):
        """Receive a single bus and return SignalGen to pulse that bus
        for n times"""
        buses = dict(clk=bus)
        period = [dict(clk=0), dict(clk=1)]
        signals = []
        for _ in range(n):
            signals.extend(period)
        return cls(buses, signals)
        
    def iterate(self):
        """Upon call returns generator object. Iteration sequentially assign
        signals in list of signals. Yield the dictionary of signals assigned"""
        for dic in self.signals:
            for label, signal in dic.items():
                self.buses[label].signal = signal
            yield dic
           
        
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

class BaseCircuitTester(unittest.TestCase):
    """
    Base class for testing circuits. Adds dry and helpful assert method
    """
    def _tester(self, circuit, truth_table):
        gen = SignalGen.sweep_circuit(circuit)
        states = [circuit.state_int for _ in gen.iterate()]
        generated_table = TruthTable(states)
        self.assertEqual(truth_table, generated_table)

    def assertSigEq(self, bus, n):
        self.assertEqual(int(bus.signal), n)

