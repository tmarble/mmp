# mmp - meta manifestparser

The purpose of mmp is to facilitate the transition from
*.ini based manifests to *.toml based manifests and
resolve Bug [1821199](https://bugzilla.mozilla.org/show_bug.cgi?id=1821199)

## Dependencies

This project depends on Python 3.10 or later and the following libraries:

* [attrs](https://pypi.org/project/attrs/)

## Usage

Set the `MOZILLA_CENTRAL` environment variable to the top source directory
for [Firefox](https://firefox-source-docs.mozilla.org/contributing/contribution_quickref.html#bootstrap-a-copy-of-the-firefox-source-code)

```
$ ./mmp.py -h
usage: Meta Manifest Parser [-h] [-v] [-t TOPSRCDIR] [-f]

options:
  -h, --help            show this help message and exit
  -v, --verbose         Prints details of each action
  -t TOPSRCDIR, --topsrcdir TOPSRCDIR
                        Path to mozilla-central
  -f, --find-ini        Identify manifestparser ini files
$
```

## Design Goals

See [DESIGN](DESIGN.md) for more background

## Acknowledgements

This project is supported by [Mozilla](https://www.mozilla.org/)

## Copyright and License

Copyright © 2023 Tom Marble

Licensed under the [MIT](http://opensource.org/licenses/MIT) [LICENSE](LICENSE)
