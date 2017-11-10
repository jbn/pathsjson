import json
import jsonschema
import os
from collections import OrderedDict
from pathsjson.resolution import Resolution
from pathsjson.helpers import *


SELF_DIR = os.path.dirname(os.path.realpath(__file__))

SCHEMA_FILE = os.path.join(SELF_DIR, "schema.json")


class PathsJSON:

    def __init__(self, file_path=None, src_dir=None, target_name=".paths.json",
                 enable_env_overrides=True, enable_user_global_overrides=True,
                 validate=True):
        if file_path is None:
            file_path = find_file_asc(src_dir, target_name)
            if file_path is None:
                raise IOError("No `{}` file found!".format(target_name))

        self._file_path = file_path
        self._enable_env_overrides = enable_env_overrides
        self._enable_user_global_overrides = enable_user_global_overrides
        self._validate = validate

        self.reload()

    def reload(self):
        """
        Reload the path definitions.
        """
        file_path = self._file_path
        enable_env_overrides = self._enable_env_overrides
        enable_user_global_overrides = self._enable_user_global_overrides
        validate = self._validate

        with open(file_path) as fp:
            data = json.load(fp, object_pairs_hook=OrderedDict)

            if '__ENV' not in data:
                data['__ENV'] = {}

            if enable_user_global_overrides:
                data = patch_with_user_globals(data)

            if enable_env_overrides:
                data = patch_with_env(data)

            inject_special_variables(data, file_path)

            if validate:
                with open(SCHEMA_FILE) as fp:
                    jsonschema.validate(data, json.load(fp))
            self._src = data
            self._paths = to_paths(expand(data))

        return self

    def __getitem__(self, args):
        if isinstance(args, tuple):
            k, args = args[0], args[1:]
        else:
            k, args = args, tuple()

        return self.resolve_path(k, *args)

    def resolve_path(self, k, *args, **kwargs):
        return self._paths[k].resolve(*args, **kwargs)

    def resolve(self, k, *args, **kwargs):
        return Resolution(self.resolve_path(k, *args, **kwargs))

    @property
    def all_resolvable_paths(self):
        paths = OrderedDict()
        for k in self._paths:
            try:
                paths[k] = self.resolve_path(k)
            except ValueError:  # Missing non-default arg
                pass
        return paths

    def _ipython_key_completions_(self):
        return list(self._paths)

    def __repr__(self):
        ks = sorted(list(self._paths))
        return "PathsJSON($keys=[{}])".format(", ".join(ks))
