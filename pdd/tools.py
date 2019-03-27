from dl import Bus

def gen_output_table(circuit, input_order=[]):
    """Return dictionary where keys are output labels and values are lists of
    signals for the given output bus based on the input (given by the index of 
    the list).
    Sequentially assign all possible values to input bus (given by 2 ** (num of inputs)),
    and record the current signal for each output"""
    if not input_order:
        input_order = circuit.input_labels
    super_bus = Bus.bus_from_buses(circuit.get_buses(input_order))
    output_buses = {label: circuit.get_bus(label) for label in circuit.output_labels}
    generated_table = {label : [] for label in circuit.output_labels}
    for signal in super_bus.sweep():
        super_bus.signal = signal
        for label, bus in output_buses.items():
            generated_table[label].append(int(bus))
    return generated_table
