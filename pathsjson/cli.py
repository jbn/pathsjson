import argparse
import json
import os
import sys
from pathsjson.impl import *


def extract_command(args):
    parser = argparse.ArgumentParser()

    parser.add_argument('--init',
                        action='store_true',
                        help='Create a .paths.json file in the cwd')

    parser.add_argument('--init-globals',
                        action='store_true',
                        help='Create the global paths.json file')

    parser.add_argument('--make-exports',
                        action='store_true',
                        help='Print exports for Makefile eval')

    parser.add_argument('--print-global-path',
                        action='store_true',
                        help='Print global paths.json file path')

    parser.add_argument('--shell-exports',
                        action='store_true',
                        help='Print exports for shell')



    args = parser.parse_args(args)

    n_set = sum(getattr(args, k) for k in dir(args) if not k.startswith('_'))

    if args.print_global_path or n_set > 1:
        print(get_user_globals_path())
        sys.exit(0)

    return args


def _main(args=None):
    args = extract_command(args)

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
    except Exception as e:
        print(e)
        sys.exit(1)


if __name__ == '__main__':
    main(sys.argv[1:])
