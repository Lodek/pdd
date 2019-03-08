
class Circuit:

    """Circuit is a base class that is inhereted to implement circuits from digital logic.

    A circuit follows the classical definition from the digital logic a black box with inputs,
    outputs and a functional specification.  A Circuit could be a simple AND gate or it could 
    be a full ALU or even processor.

    Circuit makes certain assumptions about its usage. To use Circuit one must:
    instantiate an object, assign a bus to all of its input terminals either at init
    time or later using `connect()`. That in turn creates Bus objects for the output
    terminals. Buses must not be assigned to output terminals.


    `inputs` is a list of strings with labels for the input terminals
    `outputs` is a list of string with labels for the output terminals
    `bus_lens` is a dictionary with a terminal label and a bus size
    `connections` is a dictionary with a label belonging to an internal terminal and a bus
    `bubles` is a list of strings with labels for terminal whose output will be inverted
    """
    def __init__(self, inputs, outputs, bus_lens={}, bubbles=[], connections=None):
        self.labels = {'in':inputs, 'out':outputs}
        self._set_bubbles({bubble : True for bubble in bubbles})
        self.circuits = []
        self.terminals = {}
        self.bus_lens = bus_lens
        if connections:
            self.connect(connections)

    def _set_bus_lens(self):
        """Sets a bus_len requirement on all terminals in `bus_lens`"""
        for label, length in self.bus_lens:
            self.terminals[label].bus_len = length
        
    def _set_bubbles(self, bubbles):
        """Expects a dictionary with {terminal_label : Value}
        Sets the Terminal associated to the label to Value"""
        for label, value in bubbles.items():
            self.terminals[label].invert = value
            
    def func_spec(self):
        """Function where the 'wiring' for the circuit is defined.
        In `func_spec` all gates and circuits should be instantiated and all buses
        must be assigned. func_spec is what determines what the circuit does"""
        pass
    
    def connect(self, dic):
        """Assigns buses in dic to in_bus of all Terminals defined by the `inputs`.
        Expects Dictionary of the form {label:bus} and attaches 'bus' to  'label'.
        Dictionary must contain connection for all inputs.
        """
        for label in self.labels['in']:
            if label not in dic:
                raise Exception('Connection dict does not contain all inputs')

        self.terminals = {label:Terminal() for label in inputs + outputs}
            
        #sets a bus_len to all variable buses in order to assure their length are the same
        arbitrary_inputs = [label for label in self.labels if label not in self.bus_rules]
        len_inputs = len(dic[var_buses[0]])
        for label in var_inputs:
            self.bus_rules[label] = len_inputs
        self._set_bus_lens()
        
        for label, bus in dic.items():
            self.set_bus(label, bus, 'in_bus')
                
        updater.subscribe(self, self.get_triggers())
        self._func_spec()

    def set_bus(self, label, bus, attr):
        try:
            setattr(self.terminals[label], attr, bus)
        except ValueError:
            msg = 'Failed connecting bus to label `{}` in circuit {}.' + \
                'Buses have different lengths'
            raise ValueError(msg.format(label, self.__name__))

    def connect_outputs(self, dic):
        """ """
        for label, bus in dic.items():
            if label not in self.labels['out']:
                raise Exception('Label is not an output')
            self.set_bus(label, bus, 'in_bus')

    def get_triggers(self):
        return [self.terminals[label].in_bus for label in self.labels['in']]

    def outputs(self, label):
        """Returns out_bus for the terminal associated to label"""
        return self.terminals[label].out_bus
    
    def output(self):
        """Syntatic sugar for outputs. Useful when circuit has one output
Returns the out_bus for the first out terminal."""
        label = self.labels['out'][0]
        return self.terminals[label].out_bus

    def nodes(self, label):
        """Return the Bus assosicated to the Terminal 'label' that is interior to the circuit.
eg, if terminal is an output returns in_bus,
if terminal is an input returns in_bus"""
        if label in self.labels['in']:
            bus = self.terminals[label].out_bus
        elif label in self.labels['out']:
            bus = self.terminals[label].in_bus
        else:
            raise KeyError('No "{}" label existent'.format(label))
        return bus

    def update(self):
        for label in self.labels['in']:
            self.terminals[label].propagate()

class Gate(Circuit):

    """Base class for the basic logic gates"""

    _ops = {'and':Signal.AND, 'or':Signal.OR, 'xor':Signal.XOR}
    
    def __init__(self, operation, connections={}, bubbles=[]):
        inputs = 'a b'.split()
        outputs = ['y']
        self.op = self._ops[operation]
        super().__init__(inputs, outputs, connections, bubbles)

    def _func_spec():
        y = Bus(len(self.nodes('a')))
        self.connect_outputs(self, {'y', y})
        
    def update(self):
        for label in self.labels['in']:
            self.terminals[label].propagate()
        a_sig = self.nodes['a'].signal
        b_sig = self.nodes['b'].signal
        result = self.op(a_sig, b_sig)
        self.nodes['y'].signal = result
        self.terminals['y'].propagate()


class SigGen:

    """A Signal Generator object interacts with a bus and sends signals to it."""

    pass


