import unittest, logging

class Foo:
    _ok = 0
    def getter(self): return self._ok
    def setter(self, value): self._ok = value

    attrs = {}
    attrs['bat'] = 10
    attrs['man'] = 11
    attrs['bar'] = 69
    def getter_attr(self, attr): return self.attrs[attr]
    def setter_attr(self, attr, value):
        self.attrs[attr] = value
        
    
class Test911(unittest.TestCase):

    def setUp(self):
        self.p = property(Foo.getter, Foo.setter)

    def test_instance(self):
        """Illustrates that setting a property obj to an instance doesn't work"""
        foo = Foo()
        foo.ok = self.p
        self.assertEqual(type(foo.ok), type(self.p))


    def test_progamatically(self):
        foo = Foo()
        setattr(Foo, 'ok', self.p)
        self.assertEqual(foo.ok, 0)
        
    
    def test_bar(self):
        foo = Foo()
        cls = type(foo)
        getter = lambda obj : obj.getter_attr('bar')
        setter = lambda obj, value : obj.setter_attr('bar', value)
        p = property(getter, setter)
        setattr(cls, 'bar', p)
        self.assertEqual(foo.bar, 69)
        foo.bar = 10
        self.assertEqual(foo.bar, 10)
    
    def test_set_sequence(self):
        foo = Foo()
        cls = type(foo)
        labels = 'bat man'.split()

        for label in labels:
            with self.assertRaises(AttributeError):
                getattr(foo, label)

        properties = []
        getters = []
        for label in labels:
            getter = lambda obj : obj.getter_attr(label)
            getters.append(getter)
            setter = lambda obj, value : obj.setter_attr(label, value)
            p = property(getter, setter)
            properties.append(p)
            setattr(cls, label, p)

        import pdb; pdb.set_trace()
        self.assertEqual(foo.bat, 10)
        self.assertEqual(foo.man, 11)
 
if __name__ == '__main__':
    logging.basicConfig()
    unittest.main()
