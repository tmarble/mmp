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
7. Verify that the translated TOML is legal.
