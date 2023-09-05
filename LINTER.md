# Manifest Parser Linter Guide

The purpose of this document is to specify which style conventions
are required for Manifest Parser TOML files beyond being syntactically
correct TOML.

The implementation of the Manifest Parser Linter will be
done as part of <br/>
[Bug 1847580: Update ESLint to read .toml files rather than .ini for test manifests](https://bugzilla.mozilla.org/show_bug.cgi?id=1847580)

One challenge implementing this linter for Manifest Parser TOML files
is that while all the TOML files in the tree must be syntatically valid,
the tool will have to identify which TOML files are, in fact, Manifest
Parser TOML files such that the following additional style guide
can be enforced.

## Valid TOML

As a baseline all TOML files, including Manifest Parser TOML files,
must be syntically valid.

See:

* https://toml.io/en/
* https://tomlkit.readthedocs.io/en/latest/
* https://github.com/toml-lang/toml-test

## Always includes a DEFAULT section

Each MP TOML file should include a `[DEFAULT]` section, even if empty.

## All sections should be in alphabetical order

All sections (after `[DEFAULT]`) should:

* be in alphabetical order
* have double quotes

## keyvals should have minimal whitespace

All keyvals (key = value) expressions should have exactly one
blank before and after the equals sign.

## convention for Array of strings values

All condition (`skip-if`, `supported-files`, etc.) right hand side values should
be an array of double quoted strings. If there is one string
it should be presented on one line:

```
skip-if = ["true"]
```

If there is more than one string, then each string should be
presented on it's own line (with a trailing comma):

```
skip-if = [
  "os == 'linux' && debug",
  "os == 'win'",
]
```

Every string (line) in a `*-if` (`skip-if`) value is considered
to be logically OR'd together.

## Comments for a section must appear below the section header

Comments for a section (table, file) should be _under_ the
section heading. This is important because if tooling
resorts the sections alphabetically it will maintain the comment(s)
with the proper section. For example:

```
[AAA]
# comment about section AAA
supported-files = foo.txt
```

**NOT**
```
# comment about section AAA
[AAA]
supported-files = foo.txt
```
