# Open questions on manifestparser and mmp

Here are a set of manifestparser related questions that impact the
functionalithy of **mmp**. Answers will be updated in each respective section.

## Q1 keys with no values (Illegal in TOML)?

./browser/components/about/test/unit/xpcshell.ini

What is the meaning of "head ="?
If there is no value, can it just be omitted?
Should we set the legal TOML value to '' or false or ??? Other occurances include: "dupe-manifest", "support-files", "tail"

**@ahal** says:
* Good catch, the behaviour for each case is undefined and I think we'll have to read the consumers to figure out how they are treating these. I'd guess it's ok to remove the keys, but I'm not 100% sure. I'll get back to you on this.

**@tmarble** says:
* Currently for the value in TOML I use `'' # no value from INI`
* if we decide to elide them we could preserve them in TOML as a comment

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

**@ahal** says:
* The only significance is that these keys are all "arrays" and we've decided they are useful to set in the DEFAULT section sometimes. Most of these "arrays" are delimited by any whitespace, except for skip-if which must be delimited by a newline (thus the values in this dict). This function simply concatenates the array in the DEFAULT

* If you're asking what each key is for:
   * args -> I'm not really sure
   * prefs -> test harness sets these Firefox preferences prior to running the test
   * support-files -> extra files the test requires, used by the build system to create "test packages" consumed by test tasks in CI

## Q3 implicit arrays

There are files that have, effectively, implicit arrays.

Is this the correct interpretation?

For example: ./accessible/tests/browser/events/browser.ini

https://searchfox.org/mozilla-central/source/accessible/tests/browser/events/browser.ini#3

**@ahal** says:
* Yes, these are arrays.

## Q4 fix implicit logical disjunctions

When a skip-if value has multiple lines can we safely assume they are logically OR'd together?

Example: ./accessible/tests/browser/events/browser.ini

https://searchfox.org/mozilla-central/source/accessible/tests/browser/events/browser.ini#19

**@ahal** says:
* Yes, these are logically joined by OR

## Q5 how to print text version of mp output (for copmparison)

The [documentation](https://firefox-source-docs.mozilla.org/mozbase/manifestparser.html#manifestparser-create-and-manage-test-manifests)
suggests that parsing an INI file will result in a list of test data structures.

How might we print these structures in a format that can be used to verify
that the parsed version of the TOML file (in the future) matches exactly
the parsed version of the INI file?

**@ahal** says:
* Try something like:
```
from manifestparser import ManifestParser
mp = ManifestParser(manifests=[manifests])
mp.tests  # list of test objects
```

* You could compare the Python data structure directly, or dump mp.tests to json / toml. You should also compare results when various parameters are passed in to ManifestParser.init (e.g strict=False or handle_defaults=False)

**@tmarble** says:
* I will implement this next

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
**@ahal** says:
* No I don't think so. It would be nice to not define our own expression language here, but that's a whole other project in my mind. Let's just try to keep things as is. It will be important to preserve those comments though. In your example I'd expect the TOML equivalent to be something like:
```
skip-if = [
  'os == "linux"',  # Bug 1782783
  'os == "win"',  # Bug 1818994
]
```
* (with the normal implicit OR there)

**@tmarble** says:
* You are showing the value of the skip-if to be an array (of strings). I think what we really want is for it to be an `mp_expr` BUT hoist the comment outside if it and add in the `||`

**@ahal** says:
* I'm a bit confused about your mp_expr idea.. does TOML support custom types?

**@tmarble** says:
* no. but the goal of the IR grammar is to properly identify when a value is an mp_expr -- in that way we can manipulate it properly (e.g. add the explicit ||). My thought is that, in TOML, mp_exprs will be multiline basic strings
```
"""
os == 'win'
"""
```

**@ahal** says:
* I think I might almost prefer a list of strings, as it provides a clear delineation between each skip-if annotation. if it's a multiline string, it's more of a convention

**@tmarble** says:
* this is tricky from a data type perspective... if we remove implicit stuff from INI then the the mp_expr parser can be very consistent. else we have case 1) generic expression and 2) array of expressions that are joined by logical OR

**@ahal** says:
* ah I see. maybe the logic could be pulled out of ini.py and into ManifestParser somewhere after parsing

**@tmarble** says:
* ooh yeah I like that

## Q6.5 relative paths NOT in the current directory?

Most INI files refer to files in the current directory -- in other
words the table names are filenames in the current directory.

However there are a couple of examples that agressively use relative
paths, such as ./devtools/client/framework/test/browser.ini.

https://searchfox.org/mozilla-central/source/devtools/client/framework/test/browser.ini#177

`[../../../../browser/base/content/test/static/browser_parsable_css.js]`

Should this be considered OKAY -or- should there be a series of "include:"
based MP files?

**@ahal** says:
* Yes this should be considered OK. It's a bit of a hack, but I think there are valid reasons to do this.

## Q7 The parent directive is never used

The [documentation](https://firefox-source-docs.mozilla.org/mozbase/manifestparser.html#manifest-format) mentions the parent directive `[parent:../manifest.ini]`, but
this is never used (except in internal tests).

Should this still be supported?

**@ahal** says:
* Removing this sounds good to me!

# Candidates for hand conversion to TOML

**@ahal** says:
* These all seem like good reasons to hand convert.
**@tmarble** says:
* I have added some additional cases... Q11+

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
./devtools/client/framework/test/browser.ini

`disabled=Bug 962258`

./devtools/client/inspector/boxmodel/test/browser.ini

`disabled=too many intermittent failures (bug 1009322)`


./dom/smil/test/mochitest.ini

`disabled=until bug 501183 is fixed`


## Q11 Double quotes in unquoted string

./browser/components/newtab/test/browser/abouthomecache/browser.ini
./browser/components/newtab/test/browser/browser.ini
./toolkit/components/places/tests/unit/xpcshell.ini

  `tream.feeds.section.topstories.options={"provider_name":""}`

## Q12 Unquoted value contains only one apostrophe

./netwerk/test/unit_ipc/xpcshell.ini
./services/sync/tests/unit/xpcshell.ini

  `ntially = doesn't play nice with others.`

## Q13 unusual implicit arrays

./testing/xpcshell/example/unit/xpcshell-with-prefs.ini

INI re-generated correctly, however parsing error leads to
incorrect TOML. Because RHS of pref is an unquoted-key
that gets parsed as an mp_expr --> thus all the prefs are NOT
parsed as an implicit_array

./toolkit/content/tests/chrome/chrome.ini

Unusual instance of implicit array with multiple values on one line
  `support-files = window_cursorsnap_dialog.xhtml window_cursorsnap_wizard.xhtml`

./uriloader/exthandler/tests/mochitest/browser.ini

Implicit array value contains a bracket
  `file_with[funny_name.webm`
