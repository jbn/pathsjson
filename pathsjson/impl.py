import appdirs
import copy
import json
import jsonschema
import os
from contextlib import contextmanager


SCHEMA_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                           "schema.json")


def is_env_var(s):
    return s.startswith('$$')


def is_simple_var(s):
    return s.startswith('$') and not is_env_var(s)


def path_defs_from(d):
    """
    :param d: ``.paths.json`` data structure
    :return: all path definitions without any special entries like `__ENV`
    """
    return [p for p in d.items() if p[0] != '__ENV']


def to_adjacency_list(d):
    g = {}

    for k, path in path_defs_from(d):
        g[k] = set(el[1:] for el in path if is_simple_var(el))

    return g


def to_dependents_list(g):
    deps = {}

    for k, vertices in g.items():
        for v in vertices:
            if v not in deps:
                deps[v] = set()
            deps[v].add(k)

    # I do this for deterministic ordering.
    return {k: sorted(v) for k, v in deps.items()}


def topo_sort(g, ns=None):
    ns = ns or {}
    ordering = []
    frontier = sorted([k for k, v in g.items() if not v])
    deps = to_dependents_list(g)

    while frontier:
        n = frontier.pop(0)
        ordering.append(n)
        for m in deps.get(n, []):
            g[m].remove(n)
            if not g[m]:
                frontier.append(m)

    for k, edges in g.items():
        for edge in edges:
            if edge not in ns:
                raise LookupError('Resolve failed on {}'.format(k))

    return ordering


def expand(data):
    # This makes debugging easier and safer.
    data = copy.deepcopy(data)

    g = to_adjacency_list(data)
    deps = to_dependents_list(g)
    ks = topo_sort(g, data['__ENV'])
    ns = data.pop('__ENV', {})
    expansion = {}

    for k in ks:
        path = []
        for el in data[k]:
            if is_simple_var(el):
                path.extend(ns[el[1:]])
            elif is_env_var(el):
                name = el[2:]
                path.append([name, ns.get(name)])
            else:
                path.append(el)
        ns[k] = path
        expansion[k] = ns[k]

    return expansion


def to_path_strs(expansion):
    path_strs = {}

    for k, path in expansion.items():
        parts, default_args, arg_names = [], [], []

        for el in path:
            if isinstance(el, (list, tuple)):
                parts.append("{}")
                arg_names.append(el[0])
                default_args.append(el[1])
            else:
                parts.append(el)

        path_strs[k] = (os.path.join(*parts), arg_names, default_args)

    return path_strs


def find_file_asc(src_dir=None, target_name=".paths.json", limit=None):
    """
    Walk file system towards root in search of the first target.

    :param src_dir: the directory to start from or the cwd by default.
    :param target_name: the file name to find
    :param limit: the maximum number of parent directory visits
    :return: the file path to the target or None if not found
    """
    src_dir = os.path.abspath(src_dir or os.getcwd())

    while limit is None or limit > 0:
        file_path = os.path.join(src_dir, target_name)
        if os.path.exists(file_path):
            return file_path

        next_path = os.path.dirname(src_dir)
        if next_path == src_dir:
            break
        src_dir = next_path
        if limit is not None:
            limit -= 1


def patch_with_env(data):
    for k, v in os.environ.items():
        if k in data['__ENV']:
            data['__ENV'][k] = v
        elif k in data:
            data[k] = v
    return data


def get_user_globals_path():
    return os.path.join(appdirs.user_data_dir('pathsjson'), ".paths.json")


def create_user_globals_file(overwrite=False):
    file_path = get_user_globals_path()

    if not overwrite and os.path.exists(file_path):
        raise RuntimeError("Will not overwrite: {}".format(file_path))

    dir_path = os.path.dirname(file_path)

    try:
        os.makedirs(dir_path)
    except OSError:
        pass

    with open(file_path, 'w') as fp:
        json.dump({}, fp)

    return file_path


def patch_with_user_globals(data, skip_noexist=True):
    file_path = get_user_globals_path()
    if not skip_noexist and not os.path.exists(file_path):
        raise OSError("User globals missing at: ".format(file_path))

    with open(file_path) as fp:
        global_data = json.load(fp)

    env_updates = global_data.pop('__ENV', None)
    if env_updates:
        if '__ENV' not in data:
            data['__ENV'] = env_updates
        else:
            data['__ENV'].update(env_updates)

    data.update(global_data)

    return data


class PathsJSON:

    def __init__(self, file_path=None, src_dir=None, target_name=".paths.json",
                 enable_env_overrides=True, enable_user_global_overrides=True,
                 add_implicit_root=True, validate=True):
        if file_path is None:
            file_path = find_file_asc(src_dir, target_name)
            if file_path is None:
                raise RuntimeError("No `{}` file found!".format(target_name))

        with open(file_path) as fp:
            data = json.load(fp)

            if '__ENV' not in data:
                data['__ENV'] = {}

            if enable_user_global_overrides:
                data = patch_with_user_globals(data)

            if enable_env_overrides:
                data = patch_with_env(data)

            if add_implicit_root and '_IMPLICIT_ROOT' not in data['__ENV']:
                implicit_root = os.path.abspath(os.path.dirname(file_path))
                data['__ENV']['_IMPLICIT_ROOT'] = implicit_root

            if validate:
                with open(SCHEMA_FILE) as fp:
                    jsonschema.validate(data, json.load(fp))
            self._src = data
            self._path_strs = to_path_strs(expand(data))

    def __getitem__(self, args):
        if isinstance(args, tuple):
            k, args = args[0], args[1:]
        else:
            k, args = args, tuple()

        return self.resolve_path(k, *args)

    def resolve_path(self, k, *args, **kwargs):
        # Raises a lookup error which is a reasonable.
        path, var_names, defaults = self._path_strs.get(k)

        if not var_names:
            return path

        args, path_args = list(args), []
        for name, default in zip(var_names, defaults):
            if name in kwargs:
                path_args.append(kwargs.pop(name))
            else:
                if not args:
                    if default is None:
                        expected = ", ".join(var_names)
                        raise ValueError("Expected args: {}".format(expected))
                    else:
                        path_args.append(default)
                else:
                    path_args.append(args.pop(0))

        return path.format(*path_args)

    def resolve(self, k, *args, **kwargs):
        return Resolution(self.resolve_path(k, *args, **kwargs))

    @property
    def all_resolvable_paths(self):
        paths = {}
        for k in self._path_strs:
            try:
                paths[k] = self.resolve_path(k)
            except ValueError:  # Missing non-default arg
                pass
        return paths

    def _ipython_key_completions_(self):
        return list(self._path_strs)

    def __repr__(self):
        ks = sorted(list(self._path_strs))
        return "PathsJSON(KEYS=[{}])".format(", ".join(ks))


class Resolution:
    def __init__(self, path):
        self._path = path

    @property
    def path(self):
        return self._path

    @contextmanager
    def open(self, *args, **kwargs):
        """
        Opens the file and automatically creates the directory if nessessary.
        """
        dir_path = os.path.dirname(self._path)

        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except OSError:
                pass

        with open(self._path, *args, **kwargs) as fp:
            yield fp
