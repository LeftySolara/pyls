""" pyls - list directory contents

Display information about files in the specified directory.
Uses the current directory by default.
"""

import argparse
import shutil
import textwrap
import pathlib


def process_args():
    """Specify and parse command line arguments.

    Returns
    -------
    namespace : argparse.Namespace
        Populated namespace containing argument attributes.

    """

    parser = argparse.ArgumentParser(
        prog="pyls",
        description="Display information about files in the current directory." \
            "\nUses the current directory by default.",
        usage="%(prog)s [OPTION]... [FILE]...")

    parser.add_argument(
        "-a",
        "--all",
        action='store_true',
        required=False,
        help="display all files, including hidden ones")

    parser.add_argument(
        "files",
        nargs='*',
        default='.',
        type=str,
        metavar="FILE",
        help="a space-separated list of files to display")

    namespace = parser.parse_args()
    return namespace


def print_dir_contents(dir_path, print_hidden, print_header):
    """Display the contents of the given directory.

    Parameters
    ----------
    dir_path : pathlib.Path
        Path the to directory to print.

    print_hidden : Bool
        Whether to include files whose names start with '.'

    print_header : Bool
        Whether to print the directory path as a header.

    """

    if not print_hidden:
        paths = [child for child in dir_path.iterdir() if not child.name.startswith('.')]
    else:
        paths = [child for child in dir_path.iterdir()]

    max_filename_len = len(max([path.name for path in paths], key=len))
    padded_names = [path.name.ljust(max_filename_len) for path in paths]

    column_count, row_count = shutil.get_terminal_size()
    if print_header:
        print()
        print("{}:".format(dir_path))

    print(textwrap.fill("\n".join(padded_names), column_count))


def main():
    """Main entry point for the program."""

    args = process_args()
    multiple_dirs = len(args.files) > 1

    for file in args.files:
        current_path = pathlib.Path(file)

        if not current_path.is_dir():
            print("\n{}".format(current_path))
        else:
            print_dir_contents(current_path, args.all, multiple_dirs)


if __name__ == "__main__":
    main()
