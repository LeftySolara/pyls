""" pyls - list directory contents

Display information about files in the specified directory.
Uses the current directory by default.
"""

import argparse
import datetime
import grp
import pathlib
import pwd
import shutil
import stat
import textwrap
from collections import namedtuple

FileInfo = namedtuple("FileInfo", ["filemode", "num_links", "uid", "gid",
                                    "owner", "group", "size", "timestamp", "name"])

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
        "-l",
        "--long",
        action="store_true",
        required=False,
        help="use a long listing format")

    parser.add_argument(
        "files",
        nargs='*',
        default='.',
        type=str,
        metavar="FILE",
        help="a space-separated list of files to display")

    namespace = parser.parse_args()
    return namespace


def get_file_info(file_path):
    """Fetch information about a file.

    Parameters
    ----------
    file_path : pathlib.Path
        File to gather information for.

    Returns
    -------
    info : FileInfo
        Named tuple containing file information.

    """

    filemode = stat.filemode(file_path.lstat().st_mode)
    num_hlinks = file_path.lstat().st_nlink
    size = file_path.lstat().st_size
    mtime = file_path.lstat().st_mtime

    # We have to get the user and group names from the uid and gid,
    # since path.user() and path.group() get the info for the target
    # rather than the symlink itself.
    uid = file_path.lstat().st_uid
    gid = file_path.lstat().st_gid
    owner = pwd.getpwuid(uid)[0]
    group = grp.getgrgid(gid)[0]

    name = file_path.name
    if file_path.is_symlink():
        name = "{} -> {}".format(name, file_path.resolve())

    file_year = datetime.date.fromtimestamp(mtime).year
    if file_year == datetime.date.today().year:
        timestamp = datetime.datetime.fromtimestamp(mtime).strftime("%b %d %H:%M")
    else:
        timestamp = datetime.datetime.fromtimestamp(mtime).strftime("%b %d") + " " + str(file_year).rjust(5)

    info = FileInfo(filemode, num_hlinks, uid, gid, owner, group, size, timestamp, name)
    return info


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

    paths.sort(key=lambda path: path.name.lower().strip('.'))
    max_filename_len = len(max([path.name for path in paths], key=len))
    padded_names = [path.name.ljust(max_filename_len) for path in paths]

    column_count, row_count = shutil.get_terminal_size()
    if print_header:
        print()
        print("{}:".format(dir_path))

    print(textwrap.fill("\n".join(padded_names), column_count))


def print_dir_contents_long(dir_path, print_hidden, print_header):
    """Display the contents of the given directory in long format.

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
        files = [child for child in dir_path.iterdir() if not child.name.startswith('.')]
    else:
        files = [child for child in dir_path.iterdir()]
    
    files_info = []
    for file in files:
        files_info.append(get_file_info(file))
    files_info.sort(key=lambda info: info.name.lower().strip('.'))

    # Determine the amount of padding to use for each field.
    max_links_width = len(max([str(info.num_links) for info in files_info], key=len))
    max_owner_width = len(max([info.owner for info in files_info], key=len))
    max_group_width = len(max([info.group for info in files_info], key=len))
    max_size_width = len(max([str(info.size) for info in files_info], key=len))

    padded_links = [str(info.num_links).rjust(max_links_width) for info in files_info]
    padded_owners = [info.owner.rjust(max_owner_width) for info in files_info]
    padded_goups = [info.group.rjust(max_group_width) for info in files_info]
    padded_sizes = [str(info.size).rjust(max_size_width) for info in files_info]

    for i in range(0, len(files_info)):
        print(files_info[i].filemode, padded_links[i], padded_owners[i],
              padded_goups[i], padded_sizes[i], files_info[i].timestamp, files_info[i].name)


def main():
    """Main entry point for the program."""

    args = process_args()
    multiple_dirs = len(args.files) > 1

    for file in args.files:
        current_path = pathlib.Path(file)

        if not current_path.is_dir():
            print("\n{}".format(current_path))
            continue

        if args.long:
            print_dir_contents_long(current_path, args.all, multiple_dirs)
        else:
            print_dir_contents(current_path, args.all, multiple_dirs)


if __name__ == "__main__":
    main()
