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

