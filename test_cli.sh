#!/bin/bash

###############################################################################
# setUp
###############################################################################

set -ev  # Fail on first non-zero return value.
rm -rf cli_tests/outputs && mkdir cli_tests/outputs && rm -f .paths.json

###############################################################################
# Test that automagic importing works.
###############################################################################

PWD=tests/examples/twitter python -c "from pathsjson.automagic import PATHS;"

###############################################################################
# 1. Test without any ancestral .paths.json
###############################################################################

(coverage run --source=pathsjson --append -m pathsjson.cli --shell-exports \
    > cli_tests/outputs/test_1.txt) || true

cmp -b cli_tests/outputs/test_1.txt cli_tests/test_1.expected.txt

###############################################################################
# 2. Test --shell-exports
###############################################################################

(PWD=cli_tests/full_env 
    coverage run --source=pathsjson --append -m pathsjson.cli --shell-exports \
    > cli_tests/outputs/test_2.txt) || true

diff cli_tests/outputs/test_2.txt cli_tests/test_2.expected.txt

###############################################################################
# 3. Test --make-exports
###############################################################################

(PWD=cli_tests/full_env \
    coverage run --source=pathsjson --append -m pathsjson.cli --make-exports \
    > cli_tests/outputs/test_3.txt) || true
diff cli_tests/outputs/test_3.txt cli_tests/test_3.expected.txt

###############################################################################
# 4. Test --init-global and --print-global-path
###############################################################################

(coverage run --source=pathsjson --append -m pathsjson.cli --init-global \
    > cli_tests/outputs/test_4_init_path.txt) || true

(coverage run --source=pathsjson --append -m pathsjson.cli \
    --print-global-path > cli_tests/outputs/test_4_global_path.txt)

diff \
    cli_tests/outputs/test_4_global_path.txt \
    cli_tests/outputs/test_4_init_path.txt


(PWD=cli_tests/full_env \
    coverage run --source=pathsjson --append -m pathsjson.cli --make-exports \
    > cli_tests/outputs/test_4.txt) || true

diff cli_tests/outputs/test_4.txt cli_tests/test_4.expected.txt

###############################################################################
# 5. Test --init
###############################################################################

coverage run --source=pathsjson --append -m pathsjson.cli --init

diff .paths.json cli_tests/test_5.expected.txt

rm .paths.json

###############################################################################
# tearDown
###############################################################################
rm -rf cli_tests/outputs
