#!/usr/bin/env python3
# compare-tests.py
# Copyright (c) 2023 Tom Marble
# See LICENSE for details.

import argparse
import os
import os.path
import pprint
import re
import sys

from typing import List, TextIO, Any
from attrs import define, field, validators
from deepdiff import DeepDiff
from manifestparser import ManifestParser

@define
class CompareTests:
    """
    CompareTests is the main class for the compare-tests.py program.
    """
    argv: List[str] = field(validator=validators.deep_iterable(
                                member_validator=validators.instance_of(type=str),
                                iterable_validator=validators.instance_of(type=list)),
                            default=['mmp.py'])
    errfile: TextIO = field(default=sys.stderr)
    outfile: TextIO = field(default=sys.stdout)
    topsrcdir: str = field(validator=validators.instance_of(type=str), # type: ignore
                           default='')
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
                program = 'compare-tests.py'
                self.argv = [program, '--help']
            else:
                self.argv = sys.argv
        sys.argv = self.argv
        topsrcdir: str = '.'
        if 'MOZILLA_CENTRAL' in os.environ:
            topsrcdir: str = os.environ['MOZILLA_CENTRAL']
        parser = argparse.ArgumentParser('Compare ManifestParser Tests')
        # OPTIONS ----------------------------------------
        parser.add_argument('-v', '--verbose',
                            help='Prints details of each action',
                            action='store_true', required=False)
        parser.add_argument('-o', '--output-file',
                            help='Write to file [STDOUT]',
                            default=None, required=False)
        parser.add_argument('-t', '--topsrcdir',
                            help=f'Path to mozilla-central [{topsrcdir}]',
                            default=topsrcdir, required=False)
        parser.add_argument('-I', '--ini-file',
                            help='Input INI file',
                            default=None, required=False)
        parser.add_argument('-T', '--toml-file',
                            help='Input TOML file',
                            default=None, required=False)
        # ACTIONS ----------------------------------------
        parser.add_argument('-c', '--compare',
                            help='ACTION: Compare ManifestParser Tests',
                            action='store_true', required=False)
        parser.add_argument('-d', '--dump',
                            help='ACTION: Dump ManifestParser Tests structure',
                            action='store_true', required=False)
        args: argparse.Namespace = parser.parse_args()
        self.verbose = args.verbose
        if args.output_file:
            self.outfile = open(file=args.output_file, mode='w')
        if self.verbose:
            self.err(f'compare: {args.compare}')
            self.err(f'dump: {args.dump}')
            self.err(f'ini_file: {args.ini_file}')
            self.err(f'output-file: {"STDOUT" if self.outfile == sys.stdout else args.output_file}')
            self.err(f'topsrcdir: {args.topsrcdir}')
            self.err(f'toml_file: {args.toml_file}')
        if not self.validate_topsrcdir(args.topsrcdir):
            self.err(f'topsrcdir invalid: "{args.topsrcdir}"')
            rc = 1
        elif args.compare and args.dump:
            self.err('Must specify only one action, see compare-tests.py --help')
            rc = 1
        elif args.compare:
            rc = 0 if self.compare(args.ini_file, args.toml_file) else 1
        elif args.dump:
            rc = 0 if self.dump(args.ini_file, args.toml_file) else 1
        else:
            self.err('Must specify only one action, see compare-tests.py --help')
            rc = 1
        self.outfile.close()
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

    def compare(self, ini_file: str, toml_file: str) -> bool:
        """
        Compares ManifestParser Tests
        """
        if not ini_file and not toml_file:
            self.err('Must specify both --ini-file and --toml-file')
            return False
        if ini_file.startswith('./'):
            ini_file = os.path.join(self.topsrcdir, ini_file[2:])
        if toml_file.startswith('./'):
            toml_file = os.path.join(self.topsrcdir, toml_file[2:])
        strict = True
        mp = ManifestParser(manifests=[ini_file], strict=strict, use_toml=False)
        ini_tests = mp.tests
        mp = ManifestParser(manifests=[toml_file], strict=strict, use_toml=True)
        toml_tests = mp.tests
        diff = DeepDiff(ini_tests, toml_tests)
        diff_keys = diff.keys()
        fail = False
        if len(diff_keys) == 1 and 'values_changed' in diff:
            for k in diff['values_changed'].keys():
                v = diff['values_changed'][k]
                if k.find('manifest') >= 0:
                    old_value = v['old_value']
                    new_value = v['new_value']
                    old_base, old_ext = os.path.splitext(old_value)
                    new_base, new_ext = os.path.splitext(new_value)
                    if new_base != old_base:
                        self.out(f'MANIFEST MISMATCH k={k} v={v}')
                        fail = True
                else:
                    old_value = v['old_value'].strip()
                    new_value = v['new_value'].strip()
                    if new_value != old_value:
                        old_value = re.sub(' \|\|', ' ', old_value)
                        old_value = re.sub('\s+', ' ', old_value)
                        new_value = re.sub(' \|\|', ' ', new_value)
                        new_value = re.sub('\s+', ' ', new_value)
                        if new_value != old_value:
                            self.out(f'OTHER old_value={old_value}')
                            self.out(f'      new_value={new_value}')
                            fail = True
        else:
            self.out(f'Types changed in addition to values: {diff_keys}')
            fail = True
        if fail:
            pp = pprint.PrettyPrinter(indent=2, stream=self.outfile)
            self.out('FULL DIFF')
            pp.pprint(diff)
            if self.verbose:
                self.out('=== INI ===')
                pp.pprint(ini_tests)
                self.out('=== TOML ===')
                pp.pprint(toml_tests)
            return False
        return True

    def dump(self, ini_file: str, toml_file: str) -> bool:
        """
        Dumps ManifestParser Tests
        """
        if ini_file and toml_file:
            self.err('Must specify only one of --ini-file or --toml-file')
            return False
        elif ini_file:
            filename = ini_file
            use_toml = False
        elif toml_file:
            filename = toml_file
            use_toml = True
        else:
            self.err('Must specify one of --ini-file or --toml-file')
            return False
        if filename.startswith('./'):
            filename = os.path.join(self.topsrcdir, filename[2:])
        strict = True
        mp = ManifestParser(manifests=[filename], strict=strict, use_toml=use_toml)
        pp = pprint.PrettyPrinter(indent=2, stream=self.outfile)
        self.verr(f'FILE {filename}')
        pp.pprint(mp.tests)
        return True

if __name__ == "__main__":
    sys.exit(CompareTests().run())
