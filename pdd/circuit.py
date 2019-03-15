from collections import namedtuple

class BaseCircuit:
    """
    Accepted kwargs:
    size: size of the data carrying Bus in the circuit
    bubbles: Sequence with labels for terminals whose bubble should be set
    labels (eg 'a', 'y'): Bus that will be connected to the circuit's terminals
    
    Either a data carrying Bus or size must be part of kwargs otherwise an Exception is raised
    
    """
    updater = None
    def __init__(self, **kwargs):
        #self.input_labels = []
        #self.output_labels = []
        #self.sizes = {} change me
        
        #Logic that ensures size of circuit is defined. Makes the whole thing easier
        self.labels = input_labels + output_labels
        if 'size' in kwargs:
            size = kwargs['size']
        else:
            buses = [kwargs[label] for label in self.labels if label not in self.bus_sizes and label in kwargs]
            try:
                size = len(buses[0])
            except IndexError:
                #maybe set size to 1 instead of raising an error?
                raise Exception("Need a bus or size!")
        d = {label : size for label in self.labels if label not in self.sizes}
        self.sizes.update(d)
        self.terminals = {label : Terminal(size) for label, size in self.sizes.items()}

        if bubbles in kwargs:
            self.set_bubles(**{label : True for label in bubbles})

        self.connect(**kwargs)
        self.make()

    def output(self, label=''):
        """Return Bus output bus attached to terminal `label`. If no label is given
        return the Bus of first output"""
        if not label:
            label = output_labels[0]
        return self.terminals[label].b

    def outputs(self, *args):
        """Return list with output Buses attached to terminals in args"""
        #add logic for invalid label
        return [self.terminals[label].b for label in args]

    def connect(self, **kwargs):
        for label, bus in kwargs.items():
            if label in self.input_labels:
                self.terminals[label] = Terminal(a=bus)
            elif label in self.output_labels:
                self.terminals[label] = Terminal(y=bus)
        self.update_triggers()

    def update_triggers(self):
        """Update the trigger Buses in the observer object"""
        self.updater.unsubscribe(self, self.get_inputs())
        self.updater.subscribe(self, self.get_inputs())
        

    def make(self):
        """Make must be implemented by subclasses. The body of make contain the
        the creation of circuit blocks used by the class, the association between
        these circuits and the wiring (ie connecting Bus to inputs/outputs)"""
        pass

    def get_inputs(self):
        """Return an Input object. Input objects have named attributes for each input
        in self. The value of the attribute is the same as self.terminals[label].y
        Used as syntathic sugar which eases the job of writing make()."""
        buses = {label: self.terminals[label].y for label in self.input_labels}
        return self.namedtuple_factory('Inputs', buses)

    def set_outputs(self, **kwargs):
        """Used to set the outputs of a circuit in make(). 
        kwargs keys are labels and kwargs values are buses.
        eg self.terminals['y'].a = kwargs['y']"""
        #add logic to handle case where bus doesn't exist
        for label, bus in kwargs.items():
            if label in self.output_terminals:
                self.terminals[label].a = bus 

    def set_bubbles(self, **kwargs):
        """Set bubbles in terminals present in kwargs.
        kwarg keys are labels and values is a bool"""
        #add logic to handle case where bus doesn't exist
        for key, value in kwargs.items():
            self.terminals[key].bubble = value

    def update(self):
        """Mimic the behavior of a digital circuit. Each time the voltage
        of a wire in a digital circuit changes the circuit output changes.
        update should - under normal circumstances be called by the Updater
        object automatically"""
        for label in self.input_labels:
            self.terminals[label].propagate()

    @staticmethod
    def namedtuple_factory(name, dict):
        """Factory method for namedtuples. Create a nametuple factory and
        return an instance of the factory initialized to the values in dict"""
        factory = namedtuple(name, list(dict.keys()))
        return factory(**dict)
