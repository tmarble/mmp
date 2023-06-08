#!/usr/bin/env python3
# mmp
# Copyright (c) 2023 Tom Marble
# See LICENSE for details.

import argparse
import os
import os.path
import re
import sys

from typing import List, TextIO, Any, Pattern
from attrs import define, field, validators

@define
class MetaManifestParser:
    """
    Meta Manifest Parser is the main class for the mmp program.
    """
    argv: List[str] = field(validator=validators.deep_iterable(
                                member_validator=validators.instance_of(type=str),
                                iterable_validator=validators.instance_of(type=list)),
                            default=['mmp.py'])
    errfile: TextIO = field(default=sys.stderr)
    ignore_includes: bool = field(validator=validators.instance_of(type=bool),
                                  default=False)
    match: str = field(default='(mochitest|chrome|a11y|browser|xpcshell)\x2Eini')
    regex: Pattern[str] = field(default=None)
    outfile: TextIO = field(default=sys.stdout)
    topsrcdir: str = field(validator=validators.instance_of(type=str),
                           default='')
    verbose: bool = field(validator=validators.instance_of(type=bool),
                          default=False)

    def out(self, a: Any) -> None:
        "Print to outfile (STDOUT)"
        print(a, file=self.outfile)

    def out2(self, a: Any, b: Any) -> None:
        print(a, b, file=self.outfile)

    def err(self, a: Any) -> None:
        "Print to error file (STDERR)"
        print(a, file=self.errfile)

    def err2(self, a: Any, b: Any) -> None:
        print(a, b, file=self.errfile)

    def verr(self, a: Any) -> None:
        "Print to error file (STDERR) if in verbose mode"
        if self.verbose:
            self.err(a)

    def verr2(self, a: Any, b: Any) -> None:
        if self.verbose:
            self.err2(a, b)

    def run(self) -> int:
        rc: int = 0
        program: str = os.path.basename(p=sys.argv[0])
        if len(self.argv) == 1:
            if program == 'ipykernel_launcher.py': # running in vs code
                program = 'mmp.py'
                self.argv = [program, '--help']
            else:
                self.argv = sys.argv
        sys.argv = self.argv
        parser = argparse.ArgumentParser('Meta Manifest Parser')
        parser.add_argument('-v', '--verbose',
                            help='Prints details of each action',
                            action='store_true', required=False)
        topsrcdir: str = '.'
        if 'MOZILLA_CENTRAL' in os.environ:
            topsrcdir: str = os.environ['MOZILLA_CENTRAL']
        parser.add_argument('-t', '--topsrcdir',
                            help=f'Path to mozilla-central [{topsrcdir}]',
                            default=topsrcdir, required=False)
        parser.add_argument('-f', '--find-ini',
                            help='Identify manifestparser ini files',
                            action='store_true', required=False)
        parser.add_argument('-j', '--ignore-includes',
                            help='Ignore ini files that include other ini files',
                            action='store_true', required=False)
        parser.add_argument('-m', '--match',
                            help=f'file match regex [{self.match}]',
                            default=self.match, required=False)
        args: argparse.Namespace = parser.parse_args()
        self.verbose = args.verbose
        self.ignore_includes = args.ignore_includes
        if not self.validate_topsrcdir(args.topsrcdir):
            self.err(f'topsrcdir invalid: "{args.topsrcdir}"')
            rc = 1
        if not self.validate_match(args.match):
            self.err(f'match invalid: "{args.match}"')
            rc = 1
        elif args.find_ini:
            rc = 0 if self.find_ini() else 1
        else:
            self.err('No action specified')
            rc = 1
        return rc

    def validate_topsrcdir(self, topsrcdir: str) -> bool:
        """
        Ensure topsrcdir is a valid mozilla-central directory.
        """
        (drive, tail) = os.path.splitdrive(p=topsrcdir)
        if len(tail) == 0:
            self.err('topsrcdir is empty')
            return False
        if tail[0] != os.sep:
            tail = os.path.join(os.getcwd(), tail)
        else:
            tail = drive + tail
        self.topsrcdir = os.path.normpath(tail)
        if not os.path.isdir(self.topsrcdir):
            self.err('topsrcdir is not a directory')
            return False
        mach: str = os.path.join(self.topsrcdir, 'mach')
        if not os.path.exists(mach):
            self.err('topsrcdir is not a firefox repo')
            return False
        return True

    def validate_match(self, match: str) -> bool:
        """
        Ensure match is a valid regular expression.
        """
        self.match = match
        self.regex = re.compile(match)
        return True

    def is_include(self, fullpath: str) -> bool:
        """
        Returns True if fullpath includes a section `[include`
        """
        file: TextIO = open(file=fullpath, mode="r")
        try:
            ini: str = file.read()
        except UnicodeDecodeError:
            return False
        file.close()
        return ini.find('[include:') >= 0

    def find_ini(self) -> bool:
        """
        Prints relative path of each matching *.ini file
        """
        for root, _dirs, files in os.walk(self.topsrcdir, topdown=True):
            for file in files:
                if file.endswith('.ini'):
                    fullpath: str = os.path.join(root, file)
                    path = '.' + fullpath[len(self.topsrcdir):] # make path relative
                    if not path.startswith('./obj-'): # ignore build directories
                        if self.regex.fullmatch(file):
                            self.out(path)
                        elif not self.ignore_includes and self.is_include(fullpath):
                            self.out(path)
        return True

if __name__ == "__main__":
    sys.exit(MetaManifestParser().run())
