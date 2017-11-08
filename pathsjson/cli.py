import argparse
import json
import os
import sys
from pathsjson.impl import *


def _main(args=None):
    parser = argparse.ArgumentParser()

    parser.add_argument('--print-global-path',
                        action='store_true',
                        help='Print global paths.json file path')

    parser.add_argument('--shell-exports',
                        action='store_true',
                        help='Print exports for shell')

    parser.add_argument('--make-exports',
                        action='store_true',
                        help='Print exports for Makefile eval')

    parser.add_argument('--init-globals',
                        action='store_true',
                        help='Create the global paths.json file')

    parser.add_argument('--init',
                        action='store_true',
                        help='Create a .paths.json file in the cwd')

    args = parser.parse_args(args)

    if args.print_global_path:
        print(get_user_globals_path())
        sys.exit(0)

    if args.shell_exports:
        from pathsjson.automagic import PATHS

        for k, v in PATHS.all_resolvable_paths.items():
            print('export {}="{}"'.format(k, v))
        sys.exit(0)

    # https://stackoverflow.com/questions/16656789/import-environment-settings-into-makefile-ubuntu-and-osx
    if args.make_exports:
        from pathsjson.automagic import PATHS

        for k, v in PATHS.all_resolvable_paths.items():
            print('{}?={}'.format(k, v))
        sys.exit(0)

    if args.init_globals:
        print(create_user_globals_file())
        sys.exit(0)

    if args.init:
        if os.path.exists(".paths.json"):
            raise OSError(".paths.json already exists!")

        with open(".paths.json", "w") as fp:
            json.dump({"__ENV": {}}, fp, indent=4)
            sys.exit()

    parser.print_help()


def main(args=None):
    try:
        _main(args)
    except (IOError, RuntimeError) as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
