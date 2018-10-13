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

from core import Terminal, Bus

class LogicGate:

    """Base class for the basic logic gates"""

    def __init__(self, inputs_bus):
        self.inputs = inputs_bus
        self.int_output = Bus.from_lines(len(inputs_bus[0]))
        self.output_term = Terminal(self.int_output)
        self.op = None
        
    def _func_spec(self):
        res = self.inputs[0].signal
        for sig in self.inputs[1:]:
            res = self.op(res, sig.signal)
        return res
        
    def update(self):
        res = self._func_spec()
        self.int_output.signal = res
        self.output_term.propagate()

class AND(LogicGate):

    def __init__(self, inputs_bus):
        super().__init__(inputs_bus)
        self.op = Signal.AND
