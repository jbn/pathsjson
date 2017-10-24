import os
import unittest
from pathsjson.pathsjson import *


SELF_DIR = os.path.dirname(os.path.abspath(__file__))

SAMPLE_DATA = {"ENV": {"VERSION": "1.0.0"},
               "data_dir": ["data"],
               "raw_dir": ["$data_dir", "raw"],
               "test_dir": ["$data_dir", "tests"],
               "clean_dir": ["$data_dir", "clean"],
               "codebook_dir": ["$clean_dir", "codebooks"],
               "latest_data": ["$raw_dir", "$$VERSION", "data.csv"]}


class TestPathsJson(unittest.TestCase):

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
        result = path_defs_from({'ENV': {}, 'a': 'A', 'b': 'B'})
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
        mock_leaf = os.path.join(SELF_DIR, "mock", "directory", "path")
        res = find_file_asc(mock_leaf, "test_target")
        self.assertTrue(res.endswith("test_target"))
        self.assertIsNone(find_file_asc(mock_leaf, "test_target", 1))

        # Check that it stops at root.
        import uuid
        rand_name = uuid.uuid4().hex
        self.assertIsNone(find_file_asc(mock_leaf, rand_name))


if __name__ == '__main__':
    unittest.main()
