import os
from pathsjson.impl import PathsJSON


###############################################################################
# Load the `.paths.json` file in this PWD or the ancestors of the
# PWD with (sensible) defaults.
###############################################################################
PATHS = PathsJSON(src_dir=os.environ.get('PWD', os.getcwd()))
