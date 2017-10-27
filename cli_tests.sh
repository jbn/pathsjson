#!/bin/bash

set -ev  # Fail on first non-zero return value.

PWD=tests/examples/twitter python -c "from pathsjson.automagic import PATHS;"
