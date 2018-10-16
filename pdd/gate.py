"""This module exposes the Digital Logic building blocks: AND, OR, XOR and NOT gates.
The gates are parametrized and can accept an arbitrary number of inputs in different formats.

If the gate receive a single bus as input, it will perform the operation amongst
members of the bus and produce a 1 bit output (1 line bus).

If the gate receives 2 or more n-element busses as input, the result will be
a n-element bus which operated amongst all the matching members of the busses
(eg. 3 2-bit busses, would result in a 2-bit output composed of the respective
bits for each bus).

All busses used as inputs to a single gate must have the same size (ie. same
number of lines)."""

from core import Terminal, Bus, Signal

class Gate:

    """Base class for the basic logic gates"""

    _ops = {'and':Signal.AND, 'or':Signal.OR, 'xor':Signal.XOR}
    
    def __init__(self, inputs_bus, operation, invert=[], out_bar=False):
        self.terminals = {'in' : [], 'out' : []}
        self.terminals['in'] = [Terminal(bus) for bus in inputs_bus]
        for i in invert:
            self.terminals['in'][i].invert = True
        output_in_bus = Bus.from_lines(len(inputs_bus[0]))
        self.terminals['out'] = Terminal(output_in_bus)
        self.op = self._ops[operation]


    @property
    def inputs(self):
        return [term.in_bus for term in self.terminals['in']]

    @property
    def output(self):
        return self.terminals.['out'].out_bus
        
    def _func_spec(self):
        result = self.inputs[0].output()
        for terminal in self.inputs[1:]:
            result = self.op(result, temrinal.output())
        return result
        
    def compute(self):
        output = self._func_spec()
        self.output.in_bus.signal = output
        self.output.propagate()
        

