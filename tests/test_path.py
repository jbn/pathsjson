import os
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

    def test_resolve_basic(self):
        path_str = os.path.join("data", "clean")
        path = Path(path_str)
        self.assertEqual(path.resolve(), path_str)

    def test_resolve_with_defaults(self):
        path_tmpl = os.path.join("data", "{}", "{}")
        path_str = os.path.join("data", "0.0.1", "pathsjson")
        path = Path(path_tmpl, ['VERSION', 'PROJ'], ['0.0.1', 'pathsjson'])
        self.assertEqual(path.resolve(), path_str)

    def test_resolve_with_null_default(self):
        path_tmpl = os.path.join("data", "{}")
        path = Path(path_tmpl, ['VERSION'], [None])
        with self.assertRaisesRegexp(TypeError, "Expected args"):
            path.resolve()

    def test_resolve_with_positional_overrides(self):
        path_tmpl = os.path.join("data", "{}", "{}")
        path = Path(path_tmpl, ['VERSION', 'PROJ'], ['0.0.1', 'pathsjson'])
        path_str = os.path.join("data", "0.0.2", "vaquero")
        self.assertEqual(path.resolve("0.0.2", "vaquero"), path_str)

    def test_resolve_with_keyword_overrides(self):
        path_tmpl = os.path.join("data", "{}", "{}")
        path = Path(path_tmpl, ['VERSION', 'PROJ'], ['0.0.1', 'pathsjson'])
        path_str = os.path.join("data", "0.0.2", "vaquero")
        self.assertEqual(path.resolve(PROJ="vaquero", VERSION="0.0.2"),
                         path_str)

    def test_resolve_with_too_many_args(self):
        path_tmpl = os.path.join("data", "{}", "{}")
        path = Path(path_tmpl, ['VERSION', 'PROJ'], ['0.0.1', 'pathsjson'])
        with self.assertRaisesRegexp(TypeError, "Too many args"):
            path.resolve(PROJ="vaquero", VERSION="0.0.2", MODE=1)

    def test_resolve_with_implicit_skipping(self):
        path_tmpl = os.path.join("{}", "{}")
        path = Path(path_tmpl,
                    ['_IMPLICIT_ROOT', 'PROJ'],
                    ['[implicit]', 'pathsjson'])
        path_str = os.path.join("[implicit]", "0.0.2")
        self.assertEqual(path.resolve("0.0.2"), path_str)
