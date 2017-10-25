import copy
import json
import os
import unittest
from contextlib import contextmanager

from pathsjson.impl import *


###############################################################################
# With some self-referential comedy, this is exactly the type of header that 
# paths.json removes from your code.
###############################################################################

SELF_DIR = os.path.dirname(os.path.abspath(__file__))

FIXTURES_DIR = os.path.join(SELF_DIR, "fixtures")

MOCK_LEAF = os.path.join(SELF_DIR, "mock", "directory", "path")

SAMPLE_PATH = os.path.join(FIXTURES_DIR, "sample.paths.json")

SAMPLE_DATA = json.load(open(SAMPLE_PATH))

###############################################################################


@contextmanager
def override_env(**kwargs):
    old_env = copy.deepcopy(os.environ)
    os.environ = kwargs
    try:
        yield
    finally:
        os.environ = kwargs

@contextmanager
def delete_and_replace(path):
    if os.path.exists(path):
        with open(path) as fp:
            src = fp.read()
        os.unlink(path)
        try:
            yield
        finally:
            with open(path, "w") as fp:
                fp.write(src)
    else:
        yield





###############################################################################

class TestPathsJSONFunctions(unittest.TestCase):

    def test_is_env_var(self):
        self.assertFalse(is_env_var("$CLEAN_DIR"))
        self.assertFalse(is_env_var("$data_dir"))
        self.assertTrue(is_env_var("$$VERSION"))
        self.assertFalse(is_env_var("VERSION"))

    def test_is_simple_var(self):
        self.assertTrue(is_simple_var("$CLEAN_DIR"))
        self.assertTrue(is_simple_var("$data_dir"))
        self.assertFalse(is_simple_var("$$VERSION"))
        self.assertFalse(is_simple_var("VERSION"))

    def test_path_defs_from(self):
        expected = {('a', 'A'), ('b', 'B')}
        result = path_defs_from({'__ENV': {}, 'a': 'A', 'b': 'B'})
        self.assertEqual(set(result), expected)

    def test_to_adjacency_list(self):
        result = to_adjacency_list(SAMPLE_DATA)
        expected = {"data_dir": set(),
                    "raw_dir": {"data_dir"},
                    "test_dir": {"data_dir"},
                    "clean_dir": {"data_dir"},
                    "codebook_dir": {"clean_dir"},
                    "latest_data": {"raw_dir"}}
        self.assertEqual(result, expected)

    def test_to_dependents_list(self):
        g = to_adjacency_list(SAMPLE_DATA)
        result = to_dependents_list(g)
        expected = {'clean_dir': ["codebook_dir"],
                    'data_dir': ["clean_dir", "raw_dir", "test_dir"],
                    'raw_dir': ["latest_data"]}
        self.assertEqual(result, expected)

    def test_topo_sort(self):
        g = to_adjacency_list(SAMPLE_DATA)
        result = topo_sort(g)
        expected = ['data_dir', 'clean_dir', 'raw_dir', 'test_dir',
                    'codebook_dir', 'latest_data']
        self.assertEqual(result, expected)

    def test_topo_sort_fails_on_cycle(self):
        g = to_adjacency_list({'a': "$b", 'b': "$a"})
        with self.assertRaisesRegexp(LookupError, "Resolve failed on"):
            topo_sort(g)

    def test_expand(self):
        result = expand(SAMPLE_DATA)
        expected = {"data_dir": ["data"],
                    "clean_dir": ["data", "clean"],
                    "latest_data": ["data",
                                    "raw",
                                    ["VERSION", "1.0.0"],
                                    "data.csv"],
                    "test_dir": ["data", "tests"],
                    "codebook_dir": ["data", "clean", "codebooks"],
                    "raw_dir": ["data", "raw"]}
        self.assertEqual(result, expected)

    def test_to_path_strs(self):
        path_strs = to_path_strs(expand(SAMPLE_DATA))
        expected = {"clean_dir": (os.path.join("data", "clean"), [], []),
                    "codebook_dir": (os.path.join("data", "clean", "codebooks"),
                                     [], []),
                    "latest_data": (os.path.join("data", "raw", "{}",
                                                 "data.csv"),
                                    ['VERSION'], ["1.0.0"]),
                    "data_dir": ("data", [], []),
                    "raw_dir": (os.path.join("data", "raw"), [], []),
                    "test_dir": (os.path.join("data", "tests"), [], [])}
        self.assertEqual(path_strs, expected)

    def test_find_pathsjson_file_asc(self):
        res = find_file_asc(MOCK_LEAF, "test_target")
        self.assertTrue(res.endswith("test_target"))
        self.assertIsNone(find_file_asc(MOCK_LEAF, "test_target", 1))

        # Check that it stops at root.
        import uuid
        rand_name = uuid.uuid4().hex
        self.assertIsNone(find_file_asc(MOCK_LEAF, rand_name))

    def test_patch_with_env(self):
        raw = copy.deepcopy(SAMPLE_DATA)

        with override_env(VERSION='3.1.4', raw_dir='/root'):
            data = patch_with_env(raw)
            self.assertEqual(os.environ['raw_dir'], '/root')
            self.assertEqual(data['__ENV']['VERSION'], '3.1.4')
            self.assertEqual(data['raw_dir'], '/root')

    def test_create_user_globals_file(self):
        path = get_user_globals_path()

        with delete_and_replace(path):
            create_user_globals_file()
            self.assertTrue(os.path.exists(path))
            with self.assertRaisesRegexp(RuntimeError, "Will not"):
                create_user_globals_file()

    def test_patch_with_user_globals(self):
        path = get_user_globals_path()

        with delete_and_replace(path):
            with self.assertRaisesRegexp(OSError, "User globals missing"):
                patch_with_user_globals({}, skip_noexist=False)

            expected = {'__ENV': {'ME': 'JBN'}, 'EXTRAS': '/extras'}
            create_user_globals_file()
            with open(path, 'w') as fp:
                json.dump(expected, fp)

            self.assertEqual(patch_with_user_globals({}), expected)


class TestPathsJSON(unittest.TestCase):

    def setUp(self):
        self.PATHS = PathsJSON(src_dir=FIXTURES_DIR,
                               target_name="sample.paths.json",
                               enable_user_global_overrides=False)

    def test_simple_path(self):
        self.assertEqual(self.PATHS['clean_dir'],
                         os.path.join("data", "clean"))

    def test_default_interpolation(self):
        self.assertEqual(self.PATHS['latest_data'],
                         os.path.join("data", "raw", "1.0.0", "data.csv"))

    def test_arg_override(self):
        self.assertEqual(self.PATHS['latest_data', '2.1.3'],
                         os.path.join("data", "raw", "2.1.3", "data.csv"))

    def test_resolve_kw_override(self):
        self.assertEqual(self.PATHS.resolve('latest_data', VERSION='99'),
                         os.path.join("data", "raw", "99", "data.csv"))

    def test_repr(self):
        expected = ("PathsJSON(KEYS=[clean_dir, codebook_dir, data_dir, "
                   "latest_data, raw_dir, test_dir])")
        self.assertEqual(repr(self.PATHS), expected)

    def test_implicit_root(self):
        expected = FIXTURES_DIR
        self.assertEqual(self.PATHS._src['__ENV']['_IMPLICIT_ROOT'],
                         FIXTURES_DIR)



if __name__ == '__main__':
    unittest.main()
