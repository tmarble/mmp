# Open questions on manifestparser and mmp

Here are a set of manifestparser related questions that impact the
functionalithy of **mmp**. Answers will be updated in each respective section.

## Q1 keys with no values (Illegal in TOML)?

./browser/components/about/test/unit/xpcshell.ini

What is the meaning of "head ="?
If there is no value, can it just be omitted?
Should we set the legal TOML value to '' or false or ???

Other occurances include: "dupe-manifest", "support-files", "tail"

## Q2 special treatment for DEFAULT

What is the significance of these special keys (other than `skip-if` as a
ManifestParser expression)?

```
    field_patterns = {
        "args": "%s %s",
        "prefs": "%s %s",
        "skip-if": "%s\n%s",
        "support-files": "%s %s",
    }
```

From https://searchfox.org/mozilla-central/source/testing/mozbase/manifestparser/manifestparser/ini.py#191

## Q3 implicit arrays

There are files that have, effectively, implicit arrays.

Is this the correct interpretation?

For example: ./accessible/tests/browser/events/browser.ini

https://searchfox.org/mozilla-central/source/accessible/tests/browser/events/browser.ini#3

## Q4 fix implicit logical disjunctions

When a skip-if value has multiple lines can we safely assume they are logically OR'd together?

Example: ./accessible/tests/browser/events/browser.ini

https://searchfox.org/mozilla-central/source/accessible/tests/browser/events/browser.ini#19

## Q5 how to print text version of mp output (for copmparison)

The [documentation](https://firefox-source-docs.mozilla.org/mozbase/manifestparser.html#manifestparser-create-and-manage-test-manifests)
suggests that parsing an INI file will result in a list of test data structures.

How might we print these structures in a format that can be used to verify
that the parsed version of the TOML file (in the future) matches exactly
the parsed version of the INI file?


## Q6 do we need to rewrite the mp_expr parser in manifestparser?

In particular we may want more specific power when we edit
TOML files using tomlkit (e.g. change skip-if for certain conditions).

The ManifestParser expression grammar is shown here:

https://firefox-source-docs.mozilla.org/mozbase/manifestparser.html#manifest-conditional-expressions

However, in practice, the grammer seems to be as described in the
node `mp_expr` in `ir.ebnf`.

Among other things we may want to handle comments inside mp_expr's:

```
skip-if = '''
  os == "linux"|| # Bug 1782783
  os == "win" '''  # Bug 1818994
```

## Q6 relative paths NOT in the current directory?

Most INI files refer to files in the current directory -- in other
words the table names are filenames in the current directory.

However there are a couple of examples that agressively use relative
paths, such as ./devtools/client/framework/test/browser.ini.

https://searchfox.org/mozilla-central/source/devtools/client/framework/test/browser.ini#177

`[../../../../browser/base/content/test/static/browser_parsable_css.js]`

Should this be considered OKAY -or- should there be a series of "include:"
based MP files?

## Q7 The parent directive is never used

The [documentation](https://firefox-source-docs.mozilla.org/mozbase/manifestparser.html#manifest-format) mentions the parent directive `[parent:../manifest.ini]`, but
this is never used (except in internal tests).

Should this still be supported?

# Candidates for hand conversion to TOML

## Q8 BIG implicit array?

This very large implicit array causes the Lark parser to exceed the recursion
depth and needs to be convered by hand: ./dom/media/test/mochitest.ini

https://searchfox.org/mozilla-central/source/dom/media/test/mochitest.ini#29

## Q9 Handle illegal comment

This ini file seems to have an illegal comment: ./layout/xul/test/browser.ini

```
os != 'linux' && os != 'win' // Due to testing menubar behavior with
```
https://searchfox.org/mozilla-central/source/layout/xul/test/browser.ini#10

Should that be convered to use `#` by hand?

## Q10 Handle wierd disabled, reason lines

Most disabled lines can currently be parsed, but there are some exceptions
that need to be convered by hand (by adding quotes):

./security/manager/ssl/tests/mochitest/mixedcontent/mochitest.ini
```
disabled=intermitently fails, quite often, bug 487402
```

./testing/mochitest/tests/MochiKit-1.4.2/tests/mochitest.ini

```
disabled=This test is broken: "Error: JSAN is not defined ... Line:
```

./toolkit/components/backgroundtasks/tests/xpcshell/xpcshell.ini

```
reason = Bug 1804825: code coverage harness prints [CodeCoverage] output in early startup.
```
