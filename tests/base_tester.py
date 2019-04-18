import logging, unittest, sys
path_to_codebase = '../pdd'
sys.path.append(path_to_codebase)

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



