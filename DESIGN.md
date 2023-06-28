# Design of mmp

To the degree possible the tool will leverage type annotations
in Python to increase the code reliability (_a la_ Rust) [1].
The tool will also use the attrs library to help with consistent
coding style [2] [3]. Type annotations can be supported with
the pyright libary [4] and supported in VS Code [5].
Property based testing will be driven from hypothesis [6]
which works with types, attrs and pyright [7].

Inspired by "Bug 1821207 convert .ini manifests to .toml"
I believe the design of mmp should be to be able to read *.ini or *.toml
files to an intermediate representation (IR) and write the IR
out to either *.ini or *.toml.

The existing read_ini function is not sufficient as a parser as it
ignores comments and we want to preserve comments.

Some thought was given to using an existing grammar for the input
files [8] [9] with a tool to generate a parser [10], but there
are several problems. One is that the grammar for *.ini files
is unspecified. Second the generated code almost certainly does
not use the strong typing we want for hypothesis. Third we have
identified some special cases such as preserving comments, conditional
value inheritance for the keys args, prefs, skip-if and support-files,
as well as implicit disjunctive combination of multi-line values for the
key skip-if.

The approach to developing mpp will be to:
- refine an heuristic for identifying manifestparser *.ini files
- developing an IR with readers & writers for ini & toml as inspired by
  the existing grammars and leveraging the hypothesis test tooling.
- write tests that "round trip" the IR according to Bug 1821207.
- add *.toml parsing to manifestparser as inspired by Outreachy intern
  work referenced in Bug 1779473
- write tests that compare the actual parsing output from TestManifest
  (mp.tests) from the existing *.ini parser and the new *.toml parser

## Update 1

A new parser was found, [11] Lark, which consumes EBNF and
can automatically generate a parse tree... This may very well help
construct the IR

## Update 2

Lark has turned out to be a very useful tool as a parser generator.
The first pass approach to using lark leveraged the
[LALR](https://lark-parser.readthedocs.io/en/latest/parsers.html)
parser, but that suffered from limited one token lookahead.
Instead the [Earley](https://lark-parser.readthedocs.io/en/latest/parsers.html)
parser is much more robust in resolving potential ambiguities.

The original thought about using Hypothesis for property based
testing was that it might provide strong data type definition
and example generation in similar way that the
[Spec](https://clojure.org/guides/spec) library
provides in the Clojure programming language. It appears, however,
that the library is primarily interested in simply porting
the [Quick Check](https://en.wikipedia.org/wiki/QuickCheck) functionality --
super useful in it's own right --
but does not provide the strong type support of Spec.

## References

[1] Python type annotation
    https://towardsdatascience.com/data-science-write-robust-python-with-static-typing-c71b9c9c8044

[2] attrs
    https://www.attrs.org/en/stable/

[3] attrs supports type annotations
    https://www.attrs.org/en/stable/types.html

[4] pyright
    https://github.com/microsoft/pyright

[5] pyright support in VS Code
    https://microsoft.github.io/pyright/#/

[6] hypothesis
    https://hypothesis.readthedocs.io/en/latest/
    https://github.com/HypothesisWorks/hypothesis

[7] Hypothesis supports types, attrs and pyright
    https://hypothesis.readthedocs.io/en/latest/data.html#hypothesis.strategies.from_type
    https://hypothesis.readthedocs.io/en/latest/data.html#hypothesis.strategies.builds
    https://hypothesis.readthedocs.io/en/latest/changes.html#v6-46-7

[8] *.ini grammar
    https://en.wikipedia.org/wiki/INI_file
    https://github.com/ldthomas/apg-js2-examples/blob/master/ini-file/ini-file.bnf

[9] *.toml grammar
    https://en.wikipedia.org/wiki/TOML
    https://github.com/toml-lang/toml/blob/1.0.0/toml.abnf

[10] python parser, e.g.
    https://github.com/pyparsing/pyparsing
    https://github.com/antlr/antlr4 (takes ABNF, has python generator backend)

[11] Lark
     https://github.com/lark-parser/lark
     https://lark-parser.readthedocs.io/en/latest/

## heuristic for identifying manifestparser *.ini files

This is the current heuristic for identifying *.ini files for manifest parser:

* recursively find all *.ini files starting from TOPSRCDIR.
* ignore any top level build directories (starting with `obj-`)
* consider files that have a basename that matches:
  * mochitest.ini
  * chrome.ini
  * a11y.ini
  * browser.ini
  * xpcshell.ini
* consider other *.ini files (from those that do NOT match above), but do have an include section `^\[include:`

## developing an IR

This approach will implement the `--read-ini` function using lark
