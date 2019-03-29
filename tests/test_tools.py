import unittest, logging
import truth_tables
from tools import TruthTable

class TestTruthTable(unittest.TestCase):

    def test_table(self):
        and_dicts = truth_tables.AND
        t1 = TruthTable('a b'.split(), ['y'], and_dicts)
        self.assertEqual(len(t1.table), 1)
        self.assertEqual(t1.table[0], [0, 0, 0, 1])
        
    def test_table_eq(self):
        and_dicts = truth_tables.AND
        or_dicts = truth_tables.OR

        t1 = TruthTable('a b'.split(), ['y'], and_dicts)
        t2 = TruthTable('a b'.split(), ['y'], and_dicts)
        t3 = TruthTable('a b'.split(), ['y'], or_dicts)

        self.assertEqual(t1, t2)
        self.assertNotEqual(t1, t3)

        

if __name__ == '__main__':
    logging.basicConfig(filename='{}.log'.format(__file__), filemode='w', level=logging.DEBUG)
    unittest.main()
