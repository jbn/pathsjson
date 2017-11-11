import os
from contextlib import contextmanager


class Resolution:

    def __init__(self, path_str):
        self._path_str = path_str

    @property
    def path_str(self):
        return self._path_str

    def __str__(self):
        return self._path_str

    def __repr__(self):
        return 'Resolution("{}")'.format(self.path_str)

    def __eq__(self, other):
        return self.path_str == other.path_str

    def __hash__(self):
        return hash(self.path_str)

    @contextmanager
    def open(self, *args, **kwargs):
        """
        Opens the file and automatically creates the directory if nessessary.

        :yields: the file pointer
        :param args: passed to open
        :param kwargs: passed to open
        """
        dir_path = os.path.dirname(self.path_str)

        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except OSError:
                pass

        with open(self.path_str, *args, **kwargs) as fp:
            yield fp
