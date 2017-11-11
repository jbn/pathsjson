import shutil
import unittest
from pathsjson.resolution import Resolution
from tests import *


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

    def test_open(self):
        test_dir = os.path.join(SELF_DIR, "fake_env", "open_dir")
        test_path = os.path.join(test_dir, "target.txt")

        try:
            resolution = Resolution(test_path)
            self.assertFalse(os.path.exists(test_dir))

            msg = "hello world"
            with resolution.open("w") as fp:
                fp.write(msg)

            with resolution.open("r") as fp:
                self.assertEqual(fp.read(), msg)

            msg = "goodbye world"
            with resolution.open("w") as fp:
                fp.write(msg)

            with resolution.open("r") as fp:
                self.assertEqual(fp.read(), msg)
        finally:
            shutil.rmtree(test_dir)
