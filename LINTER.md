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

All condition (`skip-if`), `supported-files`, and `prefs` right hand side values should
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

## One condition per line

Each of the mp_expr's (e.g. skip-if conditions) should
a minimal condition per line. In other words each line should
not include a logical OR `||` as each line is implicitly OR'd together.

## Comments may apply to each line

Each line an an mp_expr may have an end of line comment.
If the same Bug applies to multiple lines the comment should be
repeated on each relevant line.

## Condition simplification

Each mp_expr (e.g. skip-if condition) should be optimized as follows:

* remove extra parens (when not required by precedence rules)
* consistent whitespace within an mp_expr
* `debug == false` => `!false`
* `bits != 64` => `bits == 32`
* `os == 'win' && os_version == '10.0'` => `win10_2009`

## Remove conditions for obsolete platforms

* `skip-if = ["os != 'win' || os_version == '6.2'"]` (i.e. Windows 7 does not exist any more)
*  win/aarch64

## Remove empty right hand values

If an INI file had `support-files =` (no value) the TOML translation
would be `support-files =  '' # no value from INI` -- remove these
lines entirely.

Notable exception to this convention is `disabled = ` which should become
`disabled = true`.

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
