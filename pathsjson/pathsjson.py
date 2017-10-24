import copy
import os


def is_env_var(s):
    return s.startswith('$$')


def is_simple_var(s):
    return s.startswith('$') and not is_env_var(s)


def path_defs_from(d):
    """
    :param d: paths.json data structure
    :return: all path definitions without any special entries like `ENV`
    """
    return [p for p in d.items() if p[0] != 'ENV']


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
    ks = topo_sort(g, data['ENV'])
    ns = data.pop('ENV', {})
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


def find_file_asc(src_dir=None, target_name="paths.json", limit=None):
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
