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


def get_dir_entries(dirname, include_hidden):
    """Fetch a list of files/subdirectories in a directory.

    Parameters
    ----------
    dirname : String
        The name of the directory to search.

    include_hidden : Bool
        Whether to include files whose names start with '.'

    Returns
    -------
    files : List
        List of FileInfo objects with info about files in the given directory.

    """

    files = []
    with os.scandir(dirname) as entries:
        for entry in entries:
            files.append(get_file_info(entry))

    return files


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
            print("Error: {}. No such file or directory.".format(entry.name))

    path = entry.path
    name = entry.name
    inode = stats.st_ino
    size = stats.st_size
    mtime = stats.st_mtime
    mode = stats.st_mode
    hardlinks = stats.st_nlink
    uid = stats.st_uid
    gid = stats.st_gid

    info = FileInfo(path, name, inode, size, mtime,
                    mode, hardlinks, uid, gid)

    return info


def print_dir_contents(dir_path, print_hidden, print_header):
    """Display the contents of the given directory.

    Parameters
    ----------
    dir_path : String
        Path the to directory to print.

    print_hidden : Bool
        Whether to include files whose names start with '.'

    print_header : Bool
        Whether to print the directory path as a header.

    """

    files = get_dir_entries(dir_path, print_hidden)
    max_filename_len = len(max([file.name for file in files], key=len))
    padded_names = [file.name.ljust(max_filename_len) for file in files]

    # row_count isn't needed for what we're doing here, but we have it because
    # get_terminal_size() requires two things to assign its return values to.
    column_count, row_count = shutil.get_terminal_size()

    if print_header:
        print(dir_path + ':')
    print(textwrap.fill("\n".join(padded_names), column_count))


def main():
    """Main entry point for the program."""

    args = process_args()
    multiple_dirs = len(args.files) > 1

    for file in args.files:
        try:
            print_dir_contents(file, args.all, multiple_dirs)
            if multiple_dirs:
                print()

        except FileNotFoundError:
            print("{}: No such file or directory.\n".format(file))


if __name__ == "__main__":
    main()
