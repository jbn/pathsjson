import copy
import os
import json

from contextlib import contextmanager


###############################################################################
# With some self-referential comedy, this is exactly the type of header that
# paths.json removes from your code.
###############################################################################

SELF_DIR = os.path.dirname(os.path.abspath(__file__))

FIXTURES_DIR = os.path.join(SELF_DIR, "fixtures")

MOCK_LEAF = os.path.join(SELF_DIR, "mock", "directory", "path")

SAMPLE_PATH = os.path.join(FIXTURES_DIR, "sample.paths.json")

SAMPLE_DATA = json.load(open(SAMPLE_PATH))

TWITTER_DIR = os.path.join(SELF_DIR, "examples", "twitter")

###############################################################################


@contextmanager
def override_env(**kwargs):
    old_env = copy.deepcopy(os.environ)
    os.environ = kwargs
    try:
        yield
    finally:
        os.environ = old_env


# XXX: Add to vaquero
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
        try:
            yield
        finally:
            if os.path.exists(path):
                os.unlink(path)
