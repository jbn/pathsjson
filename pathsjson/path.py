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
        if not self.arg_names:
            return self.path

        args, path_args = list(args), []
        for name, default in zip(self.arg_names, self.defaults):
            if name in kwargs:
                path_args.append(kwargs.pop(name))
            else:
                if not args:
                    if default is None:
                        expected = ", ".join(self.arg_names)
                        raise ValueError("Expected args: {}".format(expected))
                    else:
                        path_args.append(default)
                else:
                    path_args.append(args.pop(0))

        return os.path.normpath(self.path.format(*path_args))
