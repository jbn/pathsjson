import platform
import uuid
import unittest
from tests import *
from pathsjson.impl import *


class TestPathsJSONFunctions(unittest.TestCase):

    def test_is_env_var(self):
        self.assertFalse(is_env_var("$CLEAN_DIR"))
        self.assertFalse(is_env_var("$data_dir"))
        self.assertTrue(is_env_var("$$VERSION"))
        self.assertFalse(is_env_var("VERSION"))

    def test_is_path_var(self):
        self.assertTrue(is_path_var("$CLEAN_DIR"))
        self.assertTrue(is_path_var("$data_dir"))
        self.assertFalse(is_path_var("$$VERSION"))
        self.assertFalse(is_path_var("VERSION"))

    def test_path_vars_in(self):
        expected = {('a', 'A'), ('b', 'B')}
        result = path_vars_in({'__ENV': {}, 'a': 'A', 'b': 'B'})
        self.assertEqual(set(result), expected)

    def test_to_requirements_of(self):
        result = to_requirements_of(SAMPLE_DATA)
        expected = {"DATA_DIR": set(),
                    "RAW_DIR": {"DATA_DIR"},
                    "TEST_DIR": {"DATA_DIR"},
                    "CLEAN_DIR": {"DATA_DIR"},
                    "CODEBOOK_DIR": {"CLEAN_DIR"},
                    "LATEST_DATA": {"RAW_DIR"}}
        self.assertEqual(result, expected)

    def test_to_dependencies_of(self):
        g = to_requirements_of(SAMPLE_DATA)
        result = to_dependencies_of(g)
        expected = {'CLEAN_DIR': ["CODEBOOK_DIR"],
                    'DATA_DIR': ["CLEAN_DIR", "RAW_DIR", "TEST_DIR"],
                    'RAW_DIR': ["LATEST_DATA"]}
        self.assertEqual(result, expected)

    def test_topo_sort(self):
        g = to_requirements_of(SAMPLE_DATA)
        result = topo_sort(g)
        expected = ['DATA_DIR', 'CLEAN_DIR', 'RAW_DIR', 'TEST_DIR',
                    'CODEBOOK_DIR', 'LATEST_DATA']
        self.assertEqual(result, expected)

    def test_topo_sort_fails_on_cycle(self):
        g = to_requirements_of({'a': "$b", 'b': "$a"})
        with self.assertRaisesRegexp(LookupError, "Resolve failed on"):
            topo_sort(g)

    def test_topo_sort_fails_on_unresolved(self):
        g = to_requirements_of({'a': "$b"})
        with self.assertRaisesRegexp(LookupError, "Resolve failed on"):
            topo_sort(g)

    def test_expand(self):
        result = expand(SAMPLE_DATA)

        expected = {"DATA_DIR": ["data"],
                    "CLEAN_DIR": ["data", "clean"],
                    "LATEST_DATA": ["data",
                                    "raw",
                                    ["VERSION", "1.0.0"],
                                    "data.csv"],
                    "TEST_DIR": ["data", "tests"],
                    "CODEBOOK_DIR": ["data", "clean", "codebooks"],
                    "RAW_DIR": ["data", "raw"]}
        self.assertEqual(result, expected)

    def test_expand_env_var_with_null(self):
        result = expand({'__ENV': {'VERSION': None},
                         'PATH': ['a', '$$VERSION']})

        expected = {"PATH": ["a", ['VERSION', None]]}
        self.assertEqual(result, expected)

    def test_to_paths(self):
        paths = to_paths(expand(SAMPLE_DATA))
        expected = {"CLEAN_DIR": Path(os.path.join("data", "clean")),
                    "CODEBOOK_DIR": Path(os.path.join("data", "clean",
                                                      "codebooks")),
                    "LATEST_DATA": Path(os.path.join("data", "raw", "{}",
                                                     "data.csv"),
                                        ['VERSION'], ["1.0.0"]),
                    "DATA_DIR": Path("data"),
                    "RAW_DIR": Path(os.path.join("data", "raw")),
                    "TEST_DIR": Path(os.path.join("data", "tests"))}
        self.assertEqual(paths, expected)

    def test_root_paths(self):
        data = {"__ENV": {}, "user_bin": ["$$_DRIVE_ROOT", "usr", "bin"]}
        inject_special_variables(data, FIXTURES_DIR)
        paths = to_paths(expand(data))
        path = paths['user_bin'].resolve()

        # This test is fragile.
        if platform.system().lower() == 'windows':
            self.assertEqual(path.lower(), r"c:\usr\bin")
        else:
            self.assertEqual(path, '//usr/bin')

    def test_find_pathsjson_file_asc(self):
        res = find_file_asc(MOCK_LEAF, "test_target")
        self.assertTrue(res.endswith("test_target"))
        self.assertIsNone(find_file_asc(MOCK_LEAF, "test_target", 1))

        # Check that it stops at root.
        rand_name = uuid.uuid4().hex
        self.assertIsNone(find_file_asc(MOCK_LEAF, rand_name))

    def test_patch_with_env(self):
        raw = copy.deepcopy(SAMPLE_DATA)

        with override_env(VERSION='3.1.4', RAW_DIR='/root'):
            data = patch_with_env(raw)
            self.assertEqual(os.environ['RAW_DIR'], '/root')
            self.assertEqual(data['__ENV']['VERSION'], '3.1.4')
            self.assertEqual(data['RAW_DIR'], '/root')

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
            with self.assertRaisesRegexp(IOError, "Global data missing"):
                patch_with_user_globals({}, skip_noexist=False)

            expected = {'__ENV': {'ME': 'JBN'}, 'EXTRAS': '/extras'}
            create_user_globals_file()
            with open(path, 'w') as fp:
                json.dump(expected, fp)

            self.assertEqual(patch_with_user_globals({'__ENV': {'ME': "OLD"}}),
                             expected)


class TestPathsJSON(unittest.TestCase):

    def setUp(self):
        self.PATHS = PathsJSON(src_dir=FIXTURES_DIR,
                               target_name="sample.paths.json",
                               enable_user_global_overrides=False)

    def test_bad_file_path(self):
        with self.assertRaises(IOError):
            PathsJSON(file_path=uuid.uuid4().hex)

        with self.assertRaisesRegexp(IOError, "file found"):
            PathsJSON(src_dir=MOCK_LEAF, target_name=uuid.uuid4().hex)

    def test_simple_path(self):
        self.assertEqual(self.PATHS['CLEAN_DIR'],
                         os.path.join("data", "clean"))

    def test_default_interpolation(self):
        self.assertEqual(self.PATHS['LATEST_DATA'],
                         os.path.join("data", "raw", "1.0.0", "data.csv"))

    def test_arg_override(self):
        self.assertEqual(self.PATHS['LATEST_DATA', '2.1.3'],
                         os.path.join("data", "raw", "2.1.3", "data.csv"))

    def test_resolve_path_kw_override(self):
        self.assertEqual(self.PATHS.resolve_path('LATEST_DATA', VERSION='99'),
                         os.path.join("data", "raw", "99", "data.csv"))

    def test_resolve(self):
        resolution = self.PATHS.resolve('LATEST_DATA', VERSION='99')
        self.assertEqual(resolution.path_str,
                         os.path.join("data", "raw", "99", "data.csv"))

    def test_repr(self):
        expected = ("PathsJSON($keys=[CLEAN_DIR, CODEBOOK_DIR, DATA_DIR, "
                    "LATEST_DATA, RAW_DIR, TEST_DIR])")
        self.assertEqual(repr(self.PATHS), expected)

    def test_implicit_root(self):
        self.assertEqual(self.PATHS._src['__ENV']['_IMPLICIT_ROOT'],
                         FIXTURES_DIR)

    def test_order_preservation(self):
        expected = ['DATA_DIR', 'RAW_DIR', 'TEST_DIR', 'CLEAN_DIR',
                    'LATEST_DATA', 'CODEBOOK_DIR']
        self.assertEqual(list(self.PATHS.all_resolvable_paths), expected)

    def test_works_without__env(self):
        file_path = os.path.join(FIXTURES_DIR, "paths_without_env.json")
        PATHS = PathsJSON(file_path=file_path)
        self.assertIn('__ENV', PATHS._src)

    def test_patch_with_user_globals(self):
        path = get_user_globals_path()

        with delete_and_replace(path):
            expected = {'__ENV': {'VERSION': '0'},
                        'DATA_DIR': ['root'],
                        'EXTRAS': ['extras']}
            create_user_globals_file()
            with open(path, 'w') as fp:
                json.dump(expected, fp)

            PATHS = PathsJSON(src_dir=FIXTURES_DIR,
                              target_name="sample.paths.json")
            self.assertEqual(PATHS['DATA_DIR'], 'root')
            self.assertEqual(PATHS['LATEST_DATA'],
                             os.path.join('root', 'raw', '0', 'data.csv'))

    def test_raises_key_error_on_non_existant_path(self):
        with self.assertRaises(KeyError):
            self.PATHS['missing']

    def test_with_null_defaults(self):
        PathsJSON(src_dir=FIXTURES_DIR,
                  target_name="paths_with_null_default.json")

    def test_reloading(self):
        example_path = os.path.join(MOCK_LEAF, "reloading.json")

        with delete_and_replace(example_path):
            with open(example_path, "w") as fp:
                json.dump({"ref": ["original"]}, fp)
            PATHS = PathsJSON(example_path)
            self.assertEqual(PATHS["ref"], "original")

            with open(example_path, "w") as fp:
                json.dump({"ref": ["modified"]}, fp)

            self.assertEqual(PATHS.reload()["ref"], "modified")


if __name__ == '__main__':
    unittest.main()
