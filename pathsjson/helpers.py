import appdirs
import json
import os
import copy
from collections import OrderedDict
from pathsjson.path import Path


def is_env_var(s):
    """Environmental variables have a '$$' prefix."""
    return s.startswith('$$')


def is_path_var(s):
    """Path variables start with one and only one '$'."""
    return s.startswith('$') and not is_env_var(s)


def path_vars_in(d):
    """
    Extract all (and only) the path vars in a dictionary.

    :param d: a .paths.json data structure
    :return: all path var definitions without any special entries like '__ENV'
    """
    return [p for p in d.items() if p[0] != '__ENV']


def to_requirements_of(d):
    """
    Compute the requirements of each path var.

    :param d: a .paths.json data structure
    :return: an adjacency list of the given data structure such that
        the dependency => [depends on, ...]
    """
    g = {}

    for k, path in path_vars_in(d):
        g[k] = set(el[1:] for el in path if is_path_var(el))

    return g


def to_dependencies_of(g):
    """
    Compute the dependencies of each path var.

    :param d: an adjacency list of dependency => [depends on, ...]
    :return: an adjacency list of the given data structure such that
        the k => [depends on, ...]. The vertices in the values are
        presorted to ensure reproducible results
    """
    deps = {}

    for k, vertices in g.items():
        for v in vertices:
            if v not in deps:
                deps[v] = set()
            deps[v].add(k)

    # I do this for deterministic ordering.
    return {k: sorted(v) for k, v in deps.items()}


def topo_sort(requirements, ns=None):
    """
    Topographical sort over the requirements graph.

    :param requirements: the requirements graph of a paths.json file.
    :param ns: an (optional) map of path variable to path that allows external
        bindings, e.g. a global file.
    :return: a topographical ordering suitable for processing the dependency
        graph
    """
    ns = ns or {}
    ordering = []
    frontier = sorted([k for k, v in requirements.items() if not v])
    deps = to_dependencies_of(requirements)

    while frontier:
        n = frontier.pop(0)
        ordering.append(n)
        for m in deps.get(n, []):
            requirements[m].remove(n)
            if not requirements[m]:
                frontier.append(m)

    # These are the *remaining* unresolved requirements!
    for k, edges in requirements.items():
        for edge in edges:
            if edge not in ns:
                raise LookupError('Resolve failed on {}'.format(k))

    return ordering


def expand(data):
    """
    Expand the paths.json data structure into intermediary format.

    :param data: The paths.json data structure
    :return: a mapping of path_name => [path_element, ...]. Each element is
        either a string (for path literal) or a pair of environmental variable
        name to default value.
    """
    data = copy.deepcopy(data)  # This makes debugging easier and safer.

    ns = data.pop('__ENV', {})
    ks = topo_sort(to_requirements_of(data), ns)

    # Build expansion.
    expansion = {}
    for k in ks:
        path = []

        for el in data[k]:
            if is_path_var(el):
                path.extend(ns[el[1:]])  # lookup literal
            elif is_env_var(el):
                name = el[2:]
                path.append([name, ns.get(name)])  # default binding
            else:
                path.append(el)  # simple literal

        ns[k], expansion[k] = path, path

    # Ensure sorted order for determinism.
    sorted_expansion = OrderedDict()
    for k in data:
        if k in expansion:
            sorted_expansion[k] = expansion[k]

    return sorted_expansion


def to_paths(expansion):
    """
    Converts an exanded paths.json data structure into a mapping of paths.

    :param expansion: the expansion of a paths.json data structure
    :return: a dict of path_name => Path
    """
    paths = OrderedDict()

    for k, path in expansion.items():
        parts, arg_names, default_args = [], [], []

        for el in path:
            if isinstance(el, (list, tuple)):
                parts.append("{}")
                arg_names.append(el[0])
                default_args.append(el[1])
            else:
                parts.append(el)

        paths[k] = Path(os.path.join(*parts), arg_names, default_args)

    return paths


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
    """
    Patch the paths.json data structure with environmental variables in place.

    Note this only patches *defined* paths or environmental variables.

    :param data: the paths.json data structure.
    :return: the data structure
    """
    for k, v in os.environ.items():

        if k in data['__ENV']:
            data['__ENV'][k] = v
        elif k in data:
            data[k] = v

    return data


def get_user_globals_path():
    """
    :return: the OS-dependent path to the user's global paths.json file.
    """
    return os.path.join(appdirs.user_data_dir('pathsjson'), ".paths.json")


def create_user_globals_file(overwrite=False):
    """
    Create the OS-dependent global paths.json file.

    :param overwrite: overwrites the global file if True, otherwise
        raises a RuntimeError (default)
    :return: the filepath to the created file
    """
    file_path = get_user_globals_path()

    if not overwrite and os.path.exists(file_path):
        raise RuntimeError("Will not overwrite: {}".format(file_path))

    dir_path = os.path.dirname(file_path)

    try:
        os.makedirs(dir_path)  # exist_ok is 3.x
    except OSError:
        pass

    with open(file_path, 'w') as fp:
        json.dump({}, fp)

    return file_path


def load_user_globals():
    """
    :return: the data in the user's global paths.json file or None if it
        doesn't exist
    """
    try:
        with open(get_user_globals_path()) as fp:
            return json.load(fp, object_pairs_hook=OrderedDict)
    except IOError:
        return None


def patch_with_user_globals(data, skip_noexist=True):
    """
    Patch the paths.json data structure with the user's globals in place.

    :param data: the paths.json data structure
    :param skip_noexist: skip applying global data if it doesn't exist
        otherwise raise an error for a non-existant file
    :return: the patched data
    """
    global_data = load_user_globals()

    if global_data is None:
        if skip_noexist:
            return data
        else:
            raise IOError("Global data missing and skip_no_exist=False")

    env_updates = global_data.pop('__ENV', None)
    if env_updates:
        if '__ENV' not in data:
            data['__ENV'] = env_updates
        else:
            data['__ENV'].update(env_updates)

    data.update(global_data)

    return data


def inject_special_variables(data, file_path):
    """
    Patch the paths.json data structure with special variables in place.

    :param file_path: the file path of the loaded paths.json.
    :return: the paths.json data structure
    """
    env = data['__ENV']

    if '_IMPLICIT_ROOT' not in env:
        env['_IMPLICIT_ROOT'] = os.path.abspath(os.path.dirname(file_path))

    if '_DRIVE_ROOT' not in env:
        env['_DRIVE_ROOT'] = os.path.abspath(os.sep)

    return data
