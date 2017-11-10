import os


class Path:

    def __init__(self, path, arg_names=None, defaults=None):
        self._path = path
        self._arg_names = tuple([] if arg_names is None else arg_names)
        self._defaults = tuple([] if defaults is None else defaults)

    @property
    def path(self):
        return self._path

    @property
    def arg_names(self):
        return self._arg_names

    @property
    def defaults(self):
        return self._defaults

    def __eq__(self, other):
        return (self.path == other.path and
                self.arg_names == other.arg_names and
                self.defaults == other.defaults)

    def __hash__(self):
        return hash((self.path,) + self.arg_names + self.defaults)

    def resolve(self, *args, **kwargs):
        """
        Resolve the path for use including variable interpolation.

        If there are too many parameter, resolution raises a TypeError
        (just like a function with too many parameters would raise.)
        Otherwise, it scans over the path arguments from left to right.
        During the scan, if the argument name exists in the kwargs, it's
        popped off from the kwargs. If there are more required arguments
        than there are given arguments -- both keyword and positional --
        it will try to use the defaults for all arguments prefixed with an
        underscore.

        :param args: positional arguments for interpolation
        :param kwargs: keyword-based arguments for interpolation
        :return: a path string
        """
        arg_names = self.arg_names
        n_args_expected = len(arg_names)
        if n_args_expected == 0:
            return self.path

        skip_func_args, n_args, path_args = set(), len(args) + len(kwargs), []

        if n_args < len(arg_names):
            name_strs = (x[0] if isinstance(x, list) else x for x in arg_names)
            skip_func_args = {s for s in name_strs if s.startswith('_')}

        args = list(args)

        for name, default in zip(arg_names, self.defaults):
            skip = name in skip_func_args

            if not skip and name in kwargs:
                path_args.append(kwargs.pop(name))
            elif not skip and args:
                path_args.append(args.pop(0))
            else:
                if default is None:
                    expected = ", ".join(arg_names)
                    raise TypeError("Expected args: {}".format(expected))
                else:
                    path_args.append(default)

        if args or kwargs:
            expected = ", ".join(arg_names)
            raise TypeError("Too many args. Expected: {}".format(expected))

        return os.path.normpath(self.path.format(*path_args))
