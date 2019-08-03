""" pyls - list directory contents

Display information about files in the specified directory.
Uses the current directory by default.
"""

import os
import argparse

def process_args():
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

    return parser.parse_args()

def main():
    args = process_args()

if __name__ == "__main__":
    main()