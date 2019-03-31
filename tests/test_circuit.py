import unittest, logging
from dl import Bus, BaseCircuit

class MockCircuit(BaseCircuit):
    def __init__(self, input_labels, output_labels, **kwargs):
        self.input_labels = input_labels
        self.output_labels = output_labels
        super().__init__(**kwargs)


class TestBaseCircuit(unittest.TestCase):

    def setUp(self):
        self.inputs = 'a b'.split()
        self.outputs = ['y']
        self.a = Bus(4, 10)
        self.b = Bus(4, 7)
        self.y = Bus(4, 11)
        
    def obj(self, **kwargs):
        """DRY for creating of MockCircuit with kwargs"""
        return MockCircuit(self.inputs, self.outputs, **kwargs)
    
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
        """Test Bubble setting at init"""
        obj = self.obj(size=1, bubbles=['a'])
        self.assertTrue(obj.terminals['a'].bubble)
        self.assertFalse(obj.terminals['b'].bubble)
        self.assertFalse(obj.terminals['y'].bubble)
        
    def test_bubbles_func(self):
        """Test Bubble setting through function"""
        obj = self.obj(size=1)
        obj.set_bubbles(a=True)
        self.assertTrue(obj.terminals['a'].bubble)
        self.assertFalse(obj.terminals['b'].bubble)
        self.assertFalse(obj.terminals['y'].bubble)

    def test_init_bus(self):
        a = Bus(4)
        obj = self.obj(a=a)
        for label in self.inputs:
            self.assertTrue(label in obj.terminals)
        for label in self.outputs:
            self.assertTrue(label in obj.terminals)
        terminal_lens = [term.size for term in obj.terminals.values()]
        self.assertEqual([4]*3, terminal_lens)
        
    def test_connect_init(self):
        """Test connection of Buses at init time through kwargs"""
        obj = self.obj(a=self.a, b=self.b)
        self.assertEqual(obj.terminals['a'].a, self.a)
        self.assertEqual(obj.terminals['b'].a, self.b)

    def test_connect_func(self):
        """Test connection of Buses through connect function"""
        obj = self.obj(size=4)
        obj.connect(a=self.a, b=self.b)
        self.assertEqual(obj.terminals['a'].a, self.a)
        self.assertEqual(obj.terminals['b'].a, self.b)

    def obj_bus(self, **kwargs):
        """Dry for instantiating an object with Buses"""
        return MockCircuit(self.inputs, self.outputs, a=self.a, b=self.b, **kwargs)
    
    def test_get_input(self):
        """Test that get_input return the correct Buses"""
        obj = self.obj_bus()
        obj.update()
        l = [self.a, self.b]
        inputs = [b for b in obj.get_inputs()]
        self.assertEqual(l, inputs)

    def test_set_outputs(self):
        obj = self.obj_bus()
        obj.set_outputs(y=self.y)
        self.assertEqual(obj.terminals['y'].a, self.y)
        
    def test_update_attributes(self):
        """Test the attributes in circuit corresponding to the external buses"""
        obj = self.obj_bus()
        self.assertEqual(obj.a, self.a)
        self.assertEqual(obj.b, self.b)

if __name__ == '__main__':
    logging.basicConfig(filename='core.log', filemode='w', level=logging.DEBUG)
    unittest.main()
