class MockCircuit(BaseCircuit):
    def __init__(self, input_labels, output_labels, **kwargs):
        self.input_labels = input_labels
        self.output_labels = output_labels
        super().__init__(**kwargs)


class TestBaseCircuit(unittest.TestCase):

    def setUp(self):
        self.inputs = 'a b'.split()
        self.outputs = ['y']

    def obj(self, **kwargs):
        """DRY for creating of MockCircuit with kwargs"""
        return MockCircuit(self.inputs, self.outputs, **kwargs)
    
    def test_init_fail(self):
        """Test BaseCircuit fails init when no bus or size is set"""
        with self.assertRaises(Exception):
            self.obj()

    def test_init_with_size(self):
        """Test BaseCircuit with size kwarg"""
        obj = self.obj(size=1)
        for label in self.inputs:
            self.assertTrue(label in obj.terminals)
        for label in self.outputs:
            self.assertTrue(label in obj.terminals)
        terminal_lens = [term.size for term in obj.terminals.values()]
        self.assertEqual([1]*3, terminal_lens)
        
    def test_bubbles_init(self):
        """Test Bubble setting"""
        obj = self.obj(size=1, bubbles=['a'])
        self.assertTrue(obj.terminals['a'].bubble)
        self.assertFalse(obj.terminals['b'].bubble)
        self.assertFalse(obj.terminals['y'].bubble)
        
    def test_bubbles_func(self):
        obj = self.obj(size=1)
        obj.set_bubbles(a=True)
        self.assertTrue(obj.terminals['a'].bubble)
        self.assertFalse(obj.terminals['b'].bubble)
        self.assertFalse(obj.terminals['y'].bubble)

    def 
