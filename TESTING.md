# Testing mmp

## read-toml.py to validate TOML

The `read-toml.py` program will simply parse and print out
a TOML file using the `tomklit` library.

It will exit with failure (non-zero status) if the TOML
file is invalid.

```
$ read-toml.py -h
usage: Read TOML [-h] [-v] [-o OUTPUT_FILE] [-r READ_TOML]

options:
  -h, --help            show this help message and exit
  -v, --verbose         Prints details of each action
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Write to file [STDOUT]
  -r READ_TOML, --read-toml READ_TOML
                        Read a TOML file
$
```

## tests/valid-ini to validate INI file parsing

The program `valid-ini` will:
1. Create a list of ManifestParser relevant INI files in `build/mp.txt`
2. Will skip any files listed in `tests/valid-ini-skipped.txt` (or already processed
   as listed in `build/valid-ini-passed.txt`)
3. Attempt to parse each INI file and write it out again to `build/outout.ini`
4. Record debugging/error messages in `build/outout.err`
5. If parsing is successful, it will compare the output INI file to be _exact_ match of the input (including comments and whitespace) and will fail if not matching.
6. If the parsing output passes, it will then convert the INI file to TOML
7. Verify that the translated TOML is legal. This test is useful because if
   the INI file has been improperly parsed then it will likely provoke a TOML
   syntax error.

Certain known input files that cause **mmp.py** have been skipped in:
`valid-ini-skipped.txt`. Each of these cases that require hand conversion
have been covered in [QUESTIONS](QUESTIONS.md).

```
$ export MMP=/path/to/github/tmarble/mmp
$ export PATH=$PATH:$MMP
$ ./tests/valid-ini
./accessible/tests/browser/bounds/browser.ini
./accessible/tests/browser/browser.ini
./accessible/tests/browser/e10s/browser.ini

...

./widget/windows/tests/unit/xpcshell.ini
./xpcom/tests/unit/xpcshell.ini
./xpfe/appshell/test/chrome.ini
$
```

## tests/valid-tom to validate TOML file parsing

In order to ensure that the intermediate representation (IR) grammar
properly can parse TOML we run `valid-toml` over a subset of
the TOML regression tests from: https://github.com/BurntSushi/toml-test

As **mmp.py** does not currently support certain features
(inline_table, array_table, and unicode literals) certain tests
have been omitted in: `tests/valid-toml.txt`

As **mmp.py** does not currently support whitespace around table
names one test has been skipped in:  `tests/valid-toml-skipped.txt`

```
$ cd /path/to/github
$ git clone https://github.com/BurntSushi/toml-test.git
$ export TOML_TEST=/path/to/github/toml-test
$ export MMP=/path/to/github/tmarble/mmp
$ export PATH=$PATH:$MMP
$ cd $MMP
$ ./tests/valid-toml
./tests/valid/array/array.toml
./tests/valid/array/bool.toml
./tests/valid/array/empty.toml

...

./tests/valid/table/with-pound.toml
./tests/valid/table/with-single-quotes.toml
./tests/valid/table/without-super.toml
$
```
