import argparse
import sys
from pathsjson.impl import *


def main(args=None):
    parser = argparse.ArgumentParser()

    parser.add_argument('--print-global-path',
                        action='store_true',
                        help='Print global paths.json file path')

    parser.add_argument('--shell-exports',
                        action='store_true',
                        help='Print exports for shell')

    parser.add_argument('--init-globals',
                        action='store_true',
                        help='Create the global paths.json file')

    args = parser.parse_args(args)

    if args.print_global_path:
        print(get_user_globals_path())
        sys.exit(0)

    if args.shell_exports:
        from pathsjson.automagic import PATHS

        for k, v in PATHS.all_resolvable_paths.items():
            print('export {}="{}"'.format(k, v))
        sys.exit(0)

    if args.init_globals:
        print(create_user_globals_file())
        sys.exit(0)

    parser.print_help()
