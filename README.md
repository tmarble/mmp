# mmp - meta manifestparser

The purpose of mmp is to facilitate the transition from
*.ini based manifests to *.toml based manifests and
resolve Bug [1821199](https://bugzilla.mozilla.org/show_bug.cgi?id=1821199)

## Dependencies

This project depends on Python 3.10 or later and the following libraries:

* [attrs](https://pypi.org/project/attrs/)
* [lark](https://pypi.org/project/lark/)

## Usage

Set the `MOZILLA_CENTRAL` environment variable to the top source directory
for [Firefox](https://firefox-source-docs.mozilla.org/contributing/contribution_quickref.html#bootstrap-a-copy-of-the-firefox-source-code)

There are two "ACTIONS" for mmp (all the other arguments are options):

1. `--find-ini` - will find and print a list of ManifestParser `*.ini` files in **mozilla-central**
  * will find all ini files where the basenames `--match '(mochitest|chrome|a11y|browser|xpcshell).ini'`
  * will omit ini files with **include:** directives (with `--ignore-includes`)

2. `--read-ini`- will read an ini file (relative to the root of **mozilla-central**)
  * can also read TOML!
     * Will print `== File is legal TOML? True ==` on STDERR if the input file was legal TOML
     * You can force **mmp.py** to abort if the file is NOT TOML with `--strict-toml`
  * and will write an output file to STDOUT (or to the `--output-file`)
  * in the TOML format (or INI format with `--write-ini`)
  * will show all parens around manifest parser expressions (with `--debug-expr`)
  * will fix implict manifestparser logical expressions via disjunction (with `--fix-implicit`)


```
$ ./mmp.py -h
usage: Meta Manifest Parser [-h] [-v] [-D] [-F] [-t TOPSRCDIR] [-T] [-j] [-m MATCH] [-o OUTPUT_FILE] [-W] [-f]
                            [-r READ_INI]

options:
  -h, --help            show this help message and exit
  -v, --verbose         Prints details of each action
  -D, --debug-expr      Add explicit parens around each MP expression
  -F, --fix-implicit    Fix implicit MP logical expressions
  -t TOPSRCDIR, --topsrcdir TOPSRCDIR
                        Path to mozilla-central [/home/tmarble/src/mozilla/mozilla-central]
  -T, --strict-toml     Will fail if input is not valid TOML
  -j, --ignore-includes
                        Ignore ini files that include other ini files
  -m MATCH, --match MATCH
                        file match regex [(mochitest|chrome|a11y|browser|xpcshell).ini]
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Write to file [STDOUT]
  -W, --write-ini       Write as INI
  -f, --find-ini        Identify manifestparser ini files
  -r READ_INI, --read-ini READ_INI
                        Read an ini file
$
```

### Example 1: Generate a list of manifestparser relevant ini files

```
$ export MOZILLA_CENTRAL=/path/to/mozilla-central
$ export MMP=/path/to/github/tmarble/mmp
$ export PATH=$PATH:$MMP
$ mkdir -p $MPP/build
$ cd $MOZILLA_CENTRAL
$ mmp.py --find-ini > $MPP/build/mp.txt
$  wc -l $MPP/build/mp.txt
908 $MPP/build/mp.txt
$
```
### Example 2: Read and write an ini file (they should match)

```
$ cd $MOZILLA_CENTRAL
$ mmp.py --verbose --read-ini ./accessible/tests/browser/events/browser.ini --write-ini --output-file $MMP/build/browser.ini
$ diff -u ./accessible/tests/browser/events/browser.ini $MMP/build/browser.ini
$
```

_browser.ini_
```
[DEFAULT]
subsuite = a11y
support-files =
  head.js
  !/accessible/tests/browser/shared-head.js
  !/accessible/tests/mochitest/*.js
  !/accessible/tests/browser/*.jsm
prefs =
  javascript.options.asyncstack_capture_debuggee_only=false

[browser_alert.js]
[browser_test_A11yUtils_announce.js]
[browser_test_caret_move_granularity.js]
[browser_test_docload.js]
skip-if = true
[browser_test_focus_browserui.js]
[browser_test_focus_dialog.js]
[browser_test_focus_urlbar.js]
skip-if =
  os == "linux" # Bug 1782783
  os == "win" # Bug 1818994
[browser_test_panel.js]
[browser_test_scrolling.js]
[browser_test_selection_urlbar.js]
[browser_test_textcaret.js]
```

### Example 3: Read an ini file and write the equivalent TOML file

```
$ cd $MOZILLA_CENTRAL
$ mmp.py --verbose --read-ini ./accessible/tests/browser/events/browser.ini --fix-implicit --output-file $MMP/build/browser.toml
$
```

_browser.toml_
```
[DEFAULT]
subsuite = "a11y"
support-files =[
  "head.js",
  "!/accessible/tests/browser/shared-head.js",
  "!/accessible/tests/mochitest/*.js",
  "!/accessible/tests/browser/*.jsm"]
prefs = "javascript.options.asyncstack_capture_debuggee_only=false"

[browser_alert.js]
[browser_test_A11yUtils_announce.js]
[browser_test_caret_move_granularity.js]
[browser_test_docload.js]
skip-if = true
[browser_test_focus_browserui.js]
[browser_test_focus_dialog.js]
[browser_test_focus_urlbar.js]
skip-if = '''
  os == "linux"|| # Bug 1782783
  os == "win" '''  # Bug 1818994
[browser_test_panel.js]
[browser_test_scrolling.js]
[browser_test_selection_urlbar.js]
[browser_test_textcaret.js]
```

## Documentation

See...

* [DESIGN](DESIGN.md) for more background
* [QUESTIONS](QUESTIONS.md) for open questions
* [TESTING](TESTING.md) for testing **mmp**

## Acknowledgements

This project is supported by [Mozilla](https://www.mozilla.org/)

## Copyright and License

Copyright © 2023 Tom Marble

Licensed under the [MIT](http://opensource.org/licenses/MIT) [LICENSE](LICENSE)
