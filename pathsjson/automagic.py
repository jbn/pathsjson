import os
from pathsjson.impl import PathsJSON


# Sensible default.
PATHS = PathsJSON(src_dir=os.environ.get('PWD', os.getcwd()))
