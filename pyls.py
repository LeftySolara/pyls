""" pyls - list directory contents

Display information about files in the specified directory.
Uses the current directory by default.
"""

import argparse
import os
import shutil
import textwrap
from collections import namedtuple

FileInfo = namedtuple("FileInfo", ["path", "name", "inode", "size", "mtime",
                                   "mode", "hardlinks", "uid", "gid"])

def process_args():
    """Specify and parse command line arguments."""

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


def get_file_info(entry):
    """Collect information for the given file.

    Parameters
    ----------
    entry : DirEntry
            The directory entry to collect information for.

    Returns
    -------
    info : FileInfo
           Named tuple containing file information.

    Raises
    ------
    FileNotFoundError
        If the given file does not exist.

    """

    try:
        stats = entry.stat()
    except FileNotFoundError:
        if entry.is_symlink(): # broken symlink
            stats = entry.stat(follow_symlinks=False)
        else:
            raise FileNotFoundError

    path = entry.path
    name = entry.name
    inode = stats.st_ino
    size = stats.st_size
    mtime = stats.st_mtime
    mode = stats.st_mode
    hardlinks = stats.st_nlink
    uid = stats.st_uid
    gid= stats.st_gid

    info = FileInfo(path, name, inode, size, mtime,
                    mode, hardlinks, uid, gid)

    return info


def main():
    """Main entry point for the program."""

    args = process_args()
    multiple_dirs = len(args.files) > 1
    files = []

    for file in args.files:
        with os.scandir(file) as entries:
            for entry in entries:
                files.append(get_file_info(entry))

        max_filename_len = len(max([file.name for file in files], key=len))
        padded_names = [file.name.ljust(max_filename_len) for file in files]
        column_count, row_count = shutil.get_terminal_size()

        if multiple_dirs:
            print(file + ':')
        print(textwrap.fill("\n".join(padded_names), column_count))

        if multiple_dirs:
            print()


if __name__ == "__main__":
    main()
