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
from enum import Enum, unique, auto


@unique
class Color(Enum):
    """Enumeration for colors and print formatting."""

    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


@unique
class FileType(Enum):
    """Unix file types."""

    DIR = 0        # Directory
    REG = auto()   # Regular file
    LNK = auto()   # Symbolic link
    SOCK = auto()  # Socket
    FIFO = auto()  # Named pipe
    BLK = auto()   # Block device file
    CHR = auto()   # Character special device file
    UNKNOWN = auto()   # Unknown

    # https://stackoverflow.com/questions/44595736/get-unix-file-type-with-python-os-module
    @classmethod
    def get_file_type(cls, path):
        """Get the file type of the given path."""
        if not isinstance(path, int):
            path = path.lstat().st_mode
        for path_type in cls:
            method = getattr(stat, 'S_IS' + path_type.name.upper())
            if method and method(path):
                return path_type
        return cls.UNKNOWN


class FileInfo:
    """An object in the filesystem."""

    def __init__(self, path):
        """Create a FileInfo instance and populate it with metadata.

        Parameters
        ----------
        path : string
            The path to the file. Can be relative or absolute.

        """

        self.path = pathlib.Path(path)
        self.name = self.path.name
        self.file_type = FileType.get_file_type(self.path)

        self.filemode_str = None
        self.num_links = None
        self.size = None
        self.mtime = None
        self.uid = None
        self.gid = None
        self.owner = None
        self.group = None

    def __str__(self):
        return self.name

    def get_long_info(self):
        """
        Fetch information used to print in long format. If the file is a
        symlink, get the info of the link rather than the target.

        """

        self.filemode_str = stat.filemode(self.path.lstat().st_mode)
        self.num_links = self.path.lstat().st_nlink
        self.size = self.path.lstat().st_size
        self.mtime = self.path.lstat().st_mtime

        # We have to get the user and group names from the uid and gid,
        # since path.user() and path.group() get the info for the target
        # rather than the symlink itself.
        self.uid = self.path.lstat().st_uid
        self.gid = self.path.lstat().st_gid
        self.owner = pwd.getpwuid(self.uid)[0]
        self.group = grp.getgrgid(self.gid)[0]

    def get_long_str(self, link_width=0, owner_width=0,
                     group_width=0, size_width=0):
        """Generate a string for printing in long format.

        Parameters
        ----------
        link_width : int
            Maximum width of the string representing the number of hard links.

        owner_width : int
            Maximum width of the owner name.

        group_width : int
            Maximum width of the group name.

        size_width : int
            Maximum width of the string representing the file size.

        """

        self.get_long_info()

        name = self.name
        link_padded = str(self.num_links).rjust(link_width)
        owner_padded = self.owner.rjust(owner_width)
        group_padded = self.group.rjust(group_width)
        size_padded = str(self.size).rjust(size_width)

        if self.file_type is FileType.DIR:
            name = Color.BOLD.value + Color.BLUE.value + name + Color.END.value

        if self.file_type is FileType.LNK:
            name = "{} -> {}".format(name, self.path.resolve())

        file_year = datetime.date.fromtimestamp(self.mtime).year
        this_year = datetime.date.today().year
        if file_year == this_year:
            timestamp = datetime.datetime.fromtimestamp(self.mtime).strftime("%b %d %H:%M")
        else:
            timestamp = datetime.datetime.fromtimestamp(self.mtime).strftime("%b %d") + " " + str(file_year).rjust(5)

        params = [self.filemode_str, link_padded, owner_padded, group_padded,
                  size_padded, timestamp, name]

        return " ".join(params)

    def get_children(self, include_hidden=False):
        """Get a list of files in this directory.

        Parameters
        ----------
        include_hidden: Bool
            Whether to include files whose names start with '.'

        Returns
        -------
        children : list
            List of FileInfo objects.

        """

        if not include_hidden:
            children = [FileInfo(child) for child in self.path.iterdir() if not child.name.startswith('.')]
        else:
            children = [FileInfo(child) for child in self.path.iterdir()]
        return children


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


def main():
    """Main entry point for the program."""

    args = process_args()
    # multiple_dirs = len(args.files) > 1
    files = []

    for file in args.files:
        files.append(FileInfo(file))

    if args.long:
        for file in files:
            file.get_long_info()

    max_links_width = len(max([str(file.num_links) for file in files], key=len))
    max_owner_width = len(max([file.owner for file in files], key=len))
    max_group_width = len(max([file.group for file in files], key=len))
    max_size_width = len(max([str(file.size) for file in files], key=len))

    column_count, row_count = shutil.get_terminal_size()

    if args.long:
        for file in files:
            children = file.get_children(args.all)
            children.sort(key=lambda child: child.name.lower().strip('.'))

            for child in children:
                out_str = child.get_long_str(max_links_width, max_owner_width,
                                             max_group_width, max_size_width)
                print(out_str)
    else:
        for file in files:
            children = file.get_children(args.all)
            children.sort(key=lambda child: child.name.lower().strip('.'))
            max_filename_len = len(max([child.name for child in children], key=len))
            padded_names = [child.name.ljust(max_filename_len) for child in children]
            print(textwrap.fill("\n".join(padded_names), column_count))


if __name__ == "__main__":
    main()
