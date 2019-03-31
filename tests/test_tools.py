import unittest, logging
import truth_tables
from tools import TruthTable

class TestTruthTable(unittest.TestCase):

    def test_table(self):
        t1 = truth_tables.AND
        self.assertEqual(len(t1.table), 1)
        self.assertEqual(t1.table[0], [0, 0, 0, 1])
        
    def test_table_eq(self):
        t1 = truth_tables.AND
        t2 = truth_tables.OR

        self.assertEqual(t1, t1)
        self.assertNotEqual(t1, t2)

        

if __name__ == '__main__':
    logging.basicConfig(filename='{}.log'.format(__file__), filemode='w', level=logging.DEBUG)
    unittest.main()
