import unittest
from pathsjson.path import Path


class TestPath(unittest.TestCase):

    def test_equal(self):
        a = Path('some/path', ['a', 'b', 'c'], [1, 2, 3])
        b = Path('some/path', ['a', 'b', 'c'], [1, 2, 3])
        c = Path('some/path', ['A', 'B', 'C'], [1, 2, 3])
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_hash(self):
        a = Path('some/path', ['a', 'b', 'c'], [1, 2, 3])
        b = Path('some/path', ['a', 'b', 'c'], [1, 2, 3])
        c = Path('some/path', ['A', 'B', 'C'], [1, 2, 3])
        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(hash(a), hash(c))
