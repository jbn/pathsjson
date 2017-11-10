import unittest
from pathsjson.resolution import Resolution


class TestResolution(unittest.TestCase):

    def test_str(self):
        self.assertEqual(str(Resolution("some/path")), "some/path")

    def test_repr(self):
        self.assertEqual(repr(Resolution("some/path")),
                         'Resolution("some/path")')

    def test_hash(self):
        a = Resolution("some/path")
        b = Resolution("some/path")
        c = Resolution("another/path")
        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(hash(a), hash(c))

    def test_equal(self):
        a = Resolution("some/path")
        b = Resolution("some/path")
        c = Resolution("another/path")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
