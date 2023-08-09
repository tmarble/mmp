#!/usr/bin/env python3
# read-toml.py
# Copyright (c) 2023 Tom Marble
# See LICENSE for details.

import argparse
import os
import os.path
import sys

from typing import List, TextIO, Any
from attrs import define, field, validators
from tomlkit import parse, document, dumps
from tomlkit.items import SingleKey, KeyType

@define
class ReadToml:
    """
    ReadToml is the main class for the read-toml.py program.
    """
    alpha_sort: bool = field(validator=validators.instance_of(type=bool),
                             default=False)
    argv: List[str] = field(validator=validators.deep_iterable(
                                member_validator=validators.instance_of(type=str),
                                iterable_validator=validators.instance_of(type=list)),
                            default=['mmp.py'])
    errfile: TextIO = field(default=sys.stderr)
    outfile: TextIO = field(default=sys.stdout)
    verbose: bool = field(validator=validators.instance_of(type=bool),
                          default=False)

    def out(self, a: Any, end: str = '\n') -> None:
        "Print to outfile (STDOUT)"
        print(a, file=self.outfile, end=end)

    def out2(self, a: Any, b: Any, end: str = '\n') -> None:
        print(a, b, file=self.outfile, end=end)

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
                program = 'read-toml.py'
                self.argv = [program, '--help']
            else:
                self.argv = sys.argv
        sys.argv = self.argv
        parser = argparse.ArgumentParser('Read TOML')
        # OPTIONS ----------------------------------------
        parser.add_argument('-v', '--verbose',
                            help='Prints details of each action',
                            action='store_true', required=False)
        parser.add_argument('-o', '--output-file',
                            help='Write to file [STDOUT]',
                            default=None, required=False)
        parser.add_argument('-s', '--alpha-sort',
                            help='Alpha sort TOML sections (except DEFAULT)',
                            action='store_true', required=False)
        # ACTIONS ----------------------------------------
        parser.add_argument('-r', '--read-toml',
                            help='Read a TOML file',
                            default=None, required=False)
        args: argparse.Namespace = parser.parse_args()
        self.verbose = args.verbose
        self.alpha_sort = args.alpha_sort
        if args.output_file:
            self.outfile = open(file=args.output_file, mode='w')
        if self.verbose:
            self.err(f'alpha-sort: {self.alpha_sort}')
            self.err(f'read-toml: {args.read_toml}')
            self.err(f'output-file: {"STDOUT" if self.outfile == sys.stdout else args.output_file}')
        if args.read_toml:
            rc = 0 if self.read_toml(args.read_toml) else 1
        else:
            self.err('No action specified, see read-toml.py --help')
            rc = 1
        self.outfile.close()
        return rc

    def read_binary_file_as_string(self, fullpath: str) -> str | None:
        """
        Returns contents of the file as a string (or None on error)
        """
        try:
            file = open(file=fullpath, mode="rb") # binary to preserve CRLF
        except FileNotFoundError as e:
            self.err(f'{e}')
            return None
        try:
            text: str = file.read().decode('utf-8')
        except UnicodeDecodeError:
            return None
        file.close()
        return text

    def read_toml(self, toml_file: str) -> bool:
        """
        Reads the given *.toml file
        """
        fullpath: str = toml_file
        toml: str | None = self.read_binary_file_as_string(fullpath)
        if toml == None:
            return False
        try:
            manifest = parse(toml)
            if self.alpha_sort:
                unsorted = manifest
                manifest = document()
                if 'DEFAULT' in unsorted:
                    manifest.add('DEFAULT', unsorted['DEFAULT'])
                sections = [k for k in unsorted.keys() if k != 'DEFAULT']
                for k in sorted(sections):
                    if k.find("'") >= 0:
                        section = k
                    else:
                        section = SingleKey(k, KeyType.Literal)
                    manifest.add(section, unsorted[k])
            self.out(dumps(manifest), end='')
        except Exception as e:
            self.err(f'Error: {e}')
            return False
        return True

if __name__ == "__main__":
    sys.exit(ReadToml().run())
