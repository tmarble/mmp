# Example running ini2toml

This is an example of running **ini2toml** in the context
of an actual migration. In this case these notes apply to
[Bug 1853244 convert .ini manifests to .toml: batch 6 {caps,devtools,dom}/**/browser.ini r=jmaher](https://bugzilla.mozilla.org/show_bug.cgi?id=1853244).

## Setup

For this example we are assuming running on a UNIX system in a terminal window.

As in the README certain environment variables should be set (your PATH's will likely be different):
```
export MOZILLA_CENTRAL=$HOME/src/mozilla/mozilla-central; \
export MMP=~/src/github/tmarble/mmp ; \
export PATH=$PATH:$MMP
cd $MOZILLA_CENTRAL
```

We also assume that the list of INI files for batch 6 (as mentioned in the Bug)
have been recorded in the file: `$MMP/build/mp-batch6.txt`

## Running ini2toml

When we run **ini2toml** we expect the following things will happen:
1. If necessary, it will create the `$MMP/build/mozbuild.txt` file which will help us identify which `moz.build` files need to be modified for each migrated INI
2. Each INI file will get copied to the same path with `.bak` appended
  * These files can easily be deleted after the changeset is complete by using `find . -name '*.bak'`
  * If we need to make pre-translation changes we can make them in the `*.ini.bak` file without triggering a modification of the original INI
3. The `mmp.py` program will be run to convert INI to TOML. If it fails with `FAILED to write TOML` we will examine `$MMP/build/convert.err` and likely edit the `*.ini.bak` file an try again.
4. Then the `read-toml.py` program will be run to verify that the TOML is valid and perform an alpha sort for each section. If there is a problem we will see `WROTE invalid TOML` and examine the error in `$MMP/build/sort.err`. We will edit the `*.ini.bak` file and try again.
5. It will identify which (if any) `moz.build` file refers to this INI. During the first pass we will start by creating a file `moz.build.new` and continue modifying that (because more than one INI may require edits in the same `moz.build`). In addition each `moz.build` requiring modification will be recorded in `$MMP/build/mbfiles.txt`.
6. It will then run `hg mv INI TOML` such that the INI file history may be preserved (as much as possible). The new TOML file will be written with the translated values.
7. Once all the INI files have been migrated we update all the `moz.build` files (by renaming `moz.build.new` to `moz.build`.


### run 1

```
tmarble@espoir 156 :) ini2toml $MMP/build/mp-batch6.txt
== 1 of 101 == ./caps/tests/mochitest/browser.ini
    Saving INI backup to: ./caps/tests/mochitest/browser.ini.bak
    Updating reference in ./caps/moz.build
    Saving moz.build backup to: ./caps/moz.build.bak
    MIGRATED: hg mv ./caps/tests/mochitest/browser.ini ./caps/tests/mochitest/browser.toml
== 2 of 101 == ./devtools/client/aboutdebugging/test/browser/browser.ini
    Saving INI backup to: ./devtools/client/aboutdebugging/test/browser/browser.ini.bak
    WROTE invalid TOML
```

By looking at `$MMP/build/sort.err` we see `Error: Unexpected character: ',' at line 7 col 0`. There is an extra comma. We'll move the comment onto one line following the pref and try again.

## run 2

```
tmarble@espoir 198 :( which ini2toml
/home/tmarble/src/github/tmarble/mmp/ini2toml
tmarble@espoir 199 :) ini2toml $MMP/build/mp-batch6.txt
== 1 of 101 == ./caps/tests/mochitest/browser.ini
    TOML file exists (skipping): ./caps/tests/mochitest/browser.toml
== 2 of 101 == ./devtools/client/aboutdebugging/test/browser/browser.ini
    Updating reference in ./devtools/client/aboutdebugging/moz.build
    Saving moz.build backup to: ./devtools/client/aboutdebugging/moz.build.bak
    MIGRATED: hg mv ./devtools/client/aboutdebugging/test/browser/browser.ini ./devtools/client/aboutdebugging/test/browser/browser.toml
== 3 of 101 == ./devtools/client/accessibility/test/browser/browser.ini
    Saving INI backup to: ./devtools/client/accessibility/test/browser/browser.ini.bak
    Updating reference in ./devtools/client/accessibility/moz.build
    Saving moz.build backup to: ./devtools/client/accessibility/moz.build.bak
    MIGRATED: hg mv ./devtools/client/accessibility/test/browser/browser.ini ./devtools/client/accessibility/test/browser/browser.toml
== 4 of 101 == ./devtools/client/application/test/browser/browser.ini
    Saving INI backup to: ./devtools/client/application/test/browser/browser.ini.bak
    Updating reference in ./devtools/client/application/moz.build
    Saving moz.build backup to: ./devtools/client/application/moz.build.bak
    MIGRATED: hg mv ./devtools/client/application/test/browser/browser.ini ./devtools/client/application/test/browser/browser.toml
== 5 of 101 == ./devtools/client/debugger/test/mochitest/browser.ini
    Saving INI backup to: ./devtools/client/debugger/test/mochitest/browser.ini.bak
    WROTE invalid TOML
tmarble@espoir 200 :(
```

By looking at `$MMP/build/sort.err` we see `Error: Unexpected character: ',' at line 25 col 0`. There is an extra comma. We'll move the comment onto one line following the pref and try again.

## run 3

```
tmarble@espoir 211 :) ini2toml $MMP/build/mp-batch6.txt
== 1 of 101 == ./caps/tests/mochitest/browser.ini
    TOML file exists (skipping): ./caps/tests/mochitest/browser.toml
== 2 of 101 == ./devtools/client/aboutdebugging/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/aboutdebugging/test/browser/browser.toml
== 3 of 101 == ./devtools/client/accessibility/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/accessibility/test/browser/browser.toml
== 4 of 101 == ./devtools/client/application/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/application/test/browser/browser.toml
== 5 of 101 == ./devtools/client/debugger/test/mochitest/browser.ini
    Updating reference in ./devtools/client/debugger/moz.build
    Saving moz.build backup to: ./devtools/client/debugger/moz.build.bak
    MIGRATED: hg mv ./devtools/client/debugger/test/mochitest/browser.ini ./devtools/client/debugger/test/mochitest/browser.toml
== 6 of 101 == ./devtools/client/dom/test/browser.ini
    Saving INI backup to: ./devtools/client/dom/test/browser.ini.bak
    Updating reference in ./devtools/client/dom/moz.build
    Saving moz.build backup to: ./devtools/client/dom/moz.build.bak
    MIGRATED: hg mv ./devtools/client/dom/test/browser.ini ./devtools/client/dom/test/browser.toml
== 7 of 101 == ./devtools/client/framework/browser-toolbox/test/browser.ini
    Saving INI backup to: ./devtools/client/framework/browser-toolbox/test/browser.ini.bak
    Updating reference in ./devtools/client/framework/browser-toolbox/moz.build
    Saving moz.build backup to: ./devtools/client/framework/browser-toolbox/moz.build.bak
    MIGRATED: hg mv ./devtools/client/framework/browser-toolbox/test/browser.ini ./devtools/client/framework/browser-toolbox/test/browser.toml
== 8 of 101 == ./devtools/client/framework/test/browser.ini
    Saving INI backup to: ./devtools/client/framework/test/browser.ini.bak
    FAILED to write TOML
tmarble@espoir 212 :(

```

By looking at `$MMP/build/convert.err` we see
```
parsing error: No terminal matches '
' in the current parser context, at line 138 col 20

disabled=Bug 962258
```
So the disabled value needs to be quoted

## run 4

```
tmarble@espoir 213 :) ini2toml $MMP/build/mp-batch6.txt
== 1 of 101 == ./caps/tests/mochitest/browser.ini
    TOML file exists (skipping): ./caps/tests/mochitest/browser.toml
== 2 of 101 == ./devtools/client/aboutdebugging/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/aboutdebugging/test/browser/browser.toml
== 3 of 101 == ./devtools/client/accessibility/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/accessibility/test/browser/browser.toml
== 4 of 101 == ./devtools/client/application/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/application/test/browser/browser.toml
== 5 of 101 == ./devtools/client/debugger/test/mochitest/browser.ini
    TOML file exists (skipping): ./devtools/client/debugger/test/mochitest/browser.toml
== 6 of 101 == ./devtools/client/dom/test/browser.ini
    TOML file exists (skipping): ./devtools/client/dom/test/browser.toml
== 7 of 101 == ./devtools/client/framework/browser-toolbox/test/browser.ini
    TOML file exists (skipping): ./devtools/client/framework/browser-toolbox/test/browser.toml
== 8 of 101 == ./devtools/client/framework/test/browser.ini
    Updating reference in ./devtools/client/framework/moz.build
    Saving moz.build backup to: ./devtools/client/framework/moz.build.bak
    MIGRATED: hg mv ./devtools/client/framework/test/browser.ini ./devtools/client/framework/test/browser.toml
== 9 of 101 == ./devtools/client/inspector/animation/test/browser.ini
    Saving INI backup to: ./devtools/client/inspector/animation/test/browser.ini.bak
    Updating reference in ./devtools/client/inspector/animation/moz.build
    Saving moz.build backup to: ./devtools/client/inspector/animation/moz.build.bak
    MIGRATED: hg mv ./devtools/client/inspector/animation/test/browser.ini ./devtools/client/inspector/animation/test/browser.toml
== 10 of 101 == ./devtools/client/inspector/boxmodel/test/browser.ini
    Saving INI backup to: ./devtools/client/inspector/boxmodel/test/browser.ini.bak
    FAILED to write TOML
tmarble@espoir 214 :(

```
By looking at `$MMP/build/convert.err` we see
```
parsing error: No terminal matches ')' in the current parser context, at line 18 col 53

 many intermittent failures (bug 1009322)
                                        ^
```
So the disabled value needs to be quoted (same on the last line)

## run 5

```
tmarble@espoir 217 :( ini2toml $MMP/build/mp-batch6.txt
== 1 of 101 == ./caps/tests/mochitest/browser.ini
    TOML file exists (skipping): ./caps/tests/mochitest/browser.toml
== 2 of 101 == ./devtools/client/aboutdebugging/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/aboutdebugging/test/browser/browser.toml
== 3 of 101 == ./devtools/client/accessibility/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/accessibility/test/browser/browser.toml
== 4 of 101 == ./devtools/client/application/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/application/test/browser/browser.toml
== 5 of 101 == ./devtools/client/debugger/test/mochitest/browser.ini
    TOML file exists (skipping): ./devtools/client/debugger/test/mochitest/browser.toml
== 6 of 101 == ./devtools/client/dom/test/browser.ini
    TOML file exists (skipping): ./devtools/client/dom/test/browser.toml
== 7 of 101 == ./devtools/client/framework/browser-toolbox/test/browser.ini
    TOML file exists (skipping): ./devtools/client/framework/browser-toolbox/test/browser.toml
== 8 of 101 == ./devtools/client/framework/test/browser.ini
    TOML file exists (skipping): ./devtools/client/framework/test/browser.toml
== 9 of 101 == ./devtools/client/inspector/animation/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/animation/test/browser.toml
== 10 of 101 == ./devtools/client/inspector/boxmodel/test/browser.ini
    Updating reference in ./devtools/client/inspector/boxmodel/moz.build
    Saving moz.build backup to: ./devtools/client/inspector/boxmodel/moz.build.bak
    MIGRATED: hg mv ./devtools/client/inspector/boxmodel/test/browser.ini ./devtools/client/inspector/boxmodel/test/browser.toml
== 11 of 101 == ./devtools/client/inspector/changes/test/browser.ini
    Saving INI backup to: ./devtools/client/inspector/changes/test/browser.ini.bak
    Updating reference in ./devtools/client/inspector/changes/moz.build
    Saving moz.build backup to: ./devtools/client/inspector/changes/moz.build.bak
    MIGRATED: hg mv ./devtools/client/inspector/changes/test/browser.ini ./devtools/client/inspector/changes/test/browser.toml
== 12 of 101 == ./devtools/client/inspector/compatibility/test/browser/browser.ini
    Saving INI backup to: ./devtools/client/inspector/compatibility/test/browser/browser.ini.bak
    Updating reference in ./devtools/client/inspector/compatibility/moz.build
    Saving moz.build backup to: ./devtools/client/inspector/compatibility/moz.build.bak
    MIGRATED: hg mv ./devtools/client/inspector/compatibility/test/browser/browser.ini ./devtools/client/inspector/compatibility/test/browser/browser.toml
== 13 of 101 == ./devtools/client/inspector/computed/test/browser.ini
    Saving INI backup to: ./devtools/client/inspector/computed/test/browser.ini.bak
    Updating reference in ./devtools/client/inspector/computed/moz.build
    Saving moz.build backup to: ./devtools/client/inspector/computed/moz.build.bak
    MIGRATED: hg mv ./devtools/client/inspector/computed/test/browser.ini ./devtools/client/inspector/computed/test/browser.toml
== 14 of 101 == ./devtools/client/inspector/extensions/test/browser.ini
    Saving INI backup to: ./devtools/client/inspector/extensions/test/browser.ini.bak
    Updating reference in ./devtools/client/inspector/extensions/moz.build
    Saving moz.build backup to: ./devtools/client/inspector/extensions/moz.build.bak
    MIGRATED: hg mv ./devtools/client/inspector/extensions/test/browser.ini ./devtools/client/inspector/extensions/test/browser.toml
== 15 of 101 == ./devtools/client/inspector/flexbox/test/browser.ini
    Saving INI backup to: ./devtools/client/inspector/flexbox/test/browser.ini.bak
    Updating reference in ./devtools/client/inspector/flexbox/moz.build
    Saving moz.build backup to: ./devtools/client/inspector/flexbox/moz.build.bak
    MIGRATED: hg mv ./devtools/client/inspector/flexbox/test/browser.ini ./devtools/client/inspector/flexbox/test/browser.toml
== 16 of 101 == ./devtools/client/inspector/fonts/test/browser.ini
    Saving INI backup to: ./devtools/client/inspector/fonts/test/browser.ini.bak
    Updating reference in ./devtools/client/inspector/fonts/moz.build
    Saving moz.build backup to: ./devtools/client/inspector/fonts/moz.build.bak
    MIGRATED: hg mv ./devtools/client/inspector/fonts/test/browser.ini ./devtools/client/inspector/fonts/test/browser.toml
== 17 of 101 == ./devtools/client/inspector/grids/test/browser.ini
    Saving INI backup to: ./devtools/client/inspector/grids/test/browser.ini.bak
    Updating reference in ./devtools/client/inspector/grids/moz.build
    Saving moz.build backup to: ./devtools/client/inspector/grids/moz.build.bak
    MIGRATED: hg mv ./devtools/client/inspector/grids/test/browser.ini ./devtools/client/inspector/grids/test/browser.toml
== 18 of 101 == ./devtools/client/inspector/markup/test/browser.ini
    Saving INI backup to: ./devtools/client/inspector/markup/test/browser.ini.bak
    Updating reference in ./devtools/client/inspector/markup/moz.build
    Saving moz.build backup to: ./devtools/client/inspector/markup/moz.build.bak
    MIGRATED: hg mv ./devtools/client/inspector/markup/test/browser.ini ./devtools/client/inspector/markup/test/browser.toml
== 19 of 101 == ./devtools/client/inspector/shared/test/browser.ini
    Saving INI backup to: ./devtools/client/inspector/shared/test/browser.ini.bak
    Updating reference in ./devtools/client/inspector/shared/moz.build
    Saving moz.build backup to: ./devtools/client/inspector/shared/moz.build.bak
    MIGRATED: hg mv ./devtools/client/inspector/shared/test/browser.ini ./devtools/client/inspector/shared/test/browser.toml
== 20 of 101 == ./devtools/client/inspector/test/browser.ini
    Saving INI backup to: ./devtools/client/inspector/test/browser.ini.bak
    Updating reference in ./devtools/client/inspector/moz.build
    Saving moz.build backup to: ./devtools/client/inspector/moz.build.bak
    MIGRATED: hg mv ./devtools/client/inspector/test/browser.ini ./devtools/client/inspector/test/browser.toml
== 21 of 101 == ./devtools/client/jsonview/test/browser.ini
    Saving INI backup to: ./devtools/client/jsonview/test/browser.ini.bak
    Updating reference in ./devtools/client/jsonview/moz.build
    Saving moz.build backup to: ./devtools/client/jsonview/moz.build.bak
    MIGRATED: hg mv ./devtools/client/jsonview/test/browser.ini ./devtools/client/jsonview/test/browser.toml
== 22 of 101 == ./devtools/client/memory/test/browser/browser.ini
    Saving INI backup to: ./devtools/client/memory/test/browser/browser.ini.bak
    Updating reference in ./devtools/client/memory/moz.build
    Saving moz.build backup to: ./devtools/client/memory/moz.build.bak
    MIGRATED: hg mv ./devtools/client/memory/test/browser/browser.ini ./devtools/client/memory/test/browser/browser.toml
== 23 of 101 == ./devtools/client/netmonitor/src/har/test/browser.ini
    Saving INI backup to: ./devtools/client/netmonitor/src/har/test/browser.ini.bak
    Updating reference in ./devtools/client/netmonitor/src/har/moz.build
    Saving moz.build backup to: ./devtools/client/netmonitor/src/har/moz.build.bak
    MIGRATED: hg mv ./devtools/client/netmonitor/src/har/test/browser.ini ./devtools/client/netmonitor/src/har/test/browser.toml
== 24 of 101 == ./devtools/client/netmonitor/test/browser.ini
    Saving INI backup to: ./devtools/client/netmonitor/test/browser.ini.bak
    Updating reference in ./devtools/client/netmonitor/moz.build
    Saving moz.build backup to: ./devtools/client/netmonitor/moz.build.bak
    MIGRATED: hg mv ./devtools/client/netmonitor/test/browser.ini ./devtools/client/netmonitor/test/browser.toml
== 25 of 101 == ./devtools/client/performance-new/test/browser/browser.ini
    Saving INI backup to: ./devtools/client/performance-new/test/browser/browser.ini.bak
    Updating reference in ./devtools/client/performance-new/moz.build
    Saving moz.build backup to: ./devtools/client/performance-new/moz.build.bak
    MIGRATED: hg mv ./devtools/client/performance-new/test/browser/browser.ini ./devtools/client/performance-new/test/browser/browser.toml
== 26 of 101 == ./devtools/client/responsive/test/browser/browser.ini
    Saving INI backup to: ./devtools/client/responsive/test/browser/browser.ini.bak
    Updating reference in ./devtools/client/responsive/moz.build
    Saving moz.build backup to: ./devtools/client/responsive/moz.build.bak
    MIGRATED: hg mv ./devtools/client/responsive/test/browser/browser.ini ./devtools/client/responsive/test/browser/browser.toml
== 27 of 101 == ./devtools/client/shared/components/test/browser/browser.ini
    Saving INI backup to: ./devtools/client/shared/components/test/browser/browser.ini.bak
    Updating reference in ./devtools/client/shared/components/moz.build
    Saving moz.build backup to: ./devtools/client/shared/components/moz.build.bak
    MIGRATED: hg mv ./devtools/client/shared/components/test/browser/browser.ini ./devtools/client/shared/components/test/browser/browser.toml
== 28 of 101 == ./devtools/client/shared/source-map-loader/test/browser/browser.ini
    Saving INI backup to: ./devtools/client/shared/source-map-loader/test/browser/browser.ini.bak
    Updating reference in ./devtools/client/shared/source-map-loader/moz.build
    Saving moz.build backup to: ./devtools/client/shared/source-map-loader/moz.build.bak
    MIGRATED: hg mv ./devtools/client/shared/source-map-loader/test/browser/browser.ini ./devtools/client/shared/source-map-loader/test/browser/browser.toml
== 29 of 101 == ./devtools/client/shared/sourceeditor/test/browser.ini
    Saving INI backup to: ./devtools/client/shared/sourceeditor/test/browser.ini.bak
    Updating reference in ./devtools/client/shared/sourceeditor/moz.build
    Saving moz.build backup to: ./devtools/client/shared/sourceeditor/moz.build.bak
    MIGRATED: hg mv ./devtools/client/shared/sourceeditor/test/browser.ini ./devtools/client/shared/sourceeditor/test/browser.toml
== 30 of 101 == ./devtools/client/shared/test/browser.ini
    Saving INI backup to: ./devtools/client/shared/test/browser.ini.bak
    Updating reference in ./devtools/client/shared/moz.build
    Saving moz.build backup to: ./devtools/client/shared/moz.build.bak
    MIGRATED: hg mv ./devtools/client/shared/test/browser.ini ./devtools/client/shared/test/browser.toml
== 31 of 101 == ./devtools/client/storage/test/browser.ini
    Saving INI backup to: ./devtools/client/storage/test/browser.ini.bak
    Updating reference in ./devtools/client/storage/moz.build
    Saving moz.build backup to: ./devtools/client/storage/moz.build.bak
    MIGRATED: hg mv ./devtools/client/storage/test/browser.ini ./devtools/client/storage/test/browser.toml
== 32 of 101 == ./devtools/client/styleeditor/test/browser.ini
    Saving INI backup to: ./devtools/client/styleeditor/test/browser.ini.bak
    Updating reference in ./devtools/client/styleeditor/moz.build
    Saving moz.build backup to: ./devtools/client/styleeditor/moz.build.bak
    MIGRATED: hg mv ./devtools/client/styleeditor/test/browser.ini ./devtools/client/styleeditor/test/browser.toml
== 33 of 101 == ./devtools/server/tests/browser/browser.ini
    Saving INI backup to: ./devtools/server/tests/browser/browser.ini.bak
    Updating reference in ./devtools/server/moz.build
    Saving moz.build backup to: ./devtools/server/moz.build.bak
    MIGRATED: hg mv ./devtools/server/tests/browser/browser.ini ./devtools/server/tests/browser/browser.toml
== 34 of 101 == ./devtools/server/tracer/tests/browser/browser.ini
    Saving INI backup to: ./devtools/server/tracer/tests/browser/browser.ini.bak
    Updating reference in ./devtools/server/tracer/moz.build
    Saving moz.build backup to: ./devtools/server/tracer/moz.build.bak
    MIGRATED: hg mv ./devtools/server/tracer/tests/browser/browser.ini ./devtools/server/tracer/tests/browser/browser.toml
== 35 of 101 == ./devtools/shared/commands/inspected-window/tests/browser.ini
    Saving INI backup to: ./devtools/shared/commands/inspected-window/tests/browser.ini.bak
    Updating reference in ./devtools/shared/commands/inspected-window/moz.build
    Saving moz.build backup to: ./devtools/shared/commands/inspected-window/moz.build.bak
    MIGRATED: hg mv ./devtools/shared/commands/inspected-window/tests/browser.ini ./devtools/shared/commands/inspected-window/tests/browser.toml
== 36 of 101 == ./devtools/shared/commands/inspector/tests/browser.ini
    Saving INI backup to: ./devtools/shared/commands/inspector/tests/browser.ini.bak
    Updating reference in ./devtools/shared/commands/inspector/moz.build
    Saving moz.build backup to: ./devtools/shared/commands/inspector/moz.build.bak
    MIGRATED: hg mv ./devtools/shared/commands/inspector/tests/browser.ini ./devtools/shared/commands/inspector/tests/browser.toml
== 37 of 101 == ./devtools/shared/commands/network/tests/browser.ini
    Saving INI backup to: ./devtools/shared/commands/network/tests/browser.ini.bak
    Updating reference in ./devtools/shared/commands/network/moz.build
    Saving moz.build backup to: ./devtools/shared/commands/network/moz.build.bak
    MIGRATED: hg mv ./devtools/shared/commands/network/tests/browser.ini ./devtools/shared/commands/network/tests/browser.toml
== 38 of 101 == ./devtools/shared/commands/resource/tests/browser.ini
    Saving INI backup to: ./devtools/shared/commands/resource/tests/browser.ini.bak
    Updating reference in ./devtools/shared/commands/resource/moz.build
    Saving moz.build backup to: ./devtools/shared/commands/resource/moz.build.bak
    MIGRATED: hg mv ./devtools/shared/commands/resource/tests/browser.ini ./devtools/shared/commands/resource/tests/browser.toml
== 39 of 101 == ./devtools/shared/commands/script/tests/browser.ini
    Saving INI backup to: ./devtools/shared/commands/script/tests/browser.ini.bak
    Updating reference in ./devtools/shared/commands/script/moz.build
    Saving moz.build backup to: ./devtools/shared/commands/script/moz.build.bak
    MIGRATED: hg mv ./devtools/shared/commands/script/tests/browser.ini ./devtools/shared/commands/script/tests/browser.toml
== 40 of 101 == ./devtools/shared/commands/target-configuration/tests/browser.ini
    Saving INI backup to: ./devtools/shared/commands/target-configuration/tests/browser.ini.bak
    Updating reference in ./devtools/shared/commands/target-configuration/moz.build
    Saving moz.build backup to: ./devtools/shared/commands/target-configuration/moz.build.bak
    MIGRATED: hg mv ./devtools/shared/commands/target-configuration/tests/browser.ini ./devtools/shared/commands/target-configuration/tests/browser.toml
== 41 of 101 == ./devtools/shared/commands/target/tests/browser.ini
    Saving INI backup to: ./devtools/shared/commands/target/tests/browser.ini.bak
    Updating reference in ./devtools/shared/commands/target/moz.build
    Saving moz.build backup to: ./devtools/shared/commands/target/moz.build.bak
    MIGRATED: hg mv ./devtools/shared/commands/target/tests/browser.ini ./devtools/shared/commands/target/tests/browser.toml
== 42 of 101 == ./devtools/shared/commands/thread-configuration/tests/browser.ini
    Saving INI backup to: ./devtools/shared/commands/thread-configuration/tests/browser.ini.bak
    MIGRATED: hg mv ./devtools/shared/commands/thread-configuration/tests/browser.ini ./devtools/shared/commands/thread-configuration/tests/browser.toml
== 43 of 101 == ./devtools/shared/heapsnapshot/tests/browser/browser.ini
    Saving INI backup to: ./devtools/shared/heapsnapshot/tests/browser/browser.ini.bak
    Updating reference in ./devtools/shared/heapsnapshot/moz.build
    Saving moz.build backup to: ./devtools/shared/heapsnapshot/moz.build.bak
    MIGRATED: hg mv ./devtools/shared/heapsnapshot/tests/browser/browser.ini ./devtools/shared/heapsnapshot/tests/browser/browser.toml
== 44 of 101 == ./devtools/shared/network-observer/test/browser/browser.ini
    Saving INI backup to: ./devtools/shared/network-observer/test/browser/browser.ini.bak
    Updating reference in ./devtools/shared/network-observer/moz.build
    Saving moz.build backup to: ./devtools/shared/network-observer/moz.build.bak
    MIGRATED: hg mv ./devtools/shared/network-observer/test/browser/browser.ini ./devtools/shared/network-observer/test/browser/browser.toml
== 45 of 101 == ./devtools/shared/test-helpers/browser.ini
    Saving INI backup to: ./devtools/shared/test-helpers/browser.ini.bak
    Updating reference in ./devtools/shared/moz.build
    Saving moz.build backup to: ./devtools/shared/moz.build.bak
    MIGRATED: hg mv ./devtools/shared/test-helpers/browser.ini ./devtools/shared/test-helpers/browser.toml
== 46 of 101 == ./devtools/shared/tests/browser/browser.ini
    Saving INI backup to: ./devtools/shared/tests/browser/browser.ini.bak
    Updating reference in ./devtools/shared/moz.build
    MIGRATED: hg mv ./devtools/shared/tests/browser/browser.ini ./devtools/shared/tests/browser/browser.toml
== 47 of 101 == ./devtools/shared/webconsole/test/browser/browser.ini
    Saving INI backup to: ./devtools/shared/webconsole/test/browser/browser.ini.bak
    Updating reference in ./devtools/shared/webconsole/moz.build
    Saving moz.build backup to: ./devtools/shared/webconsole/moz.build.bak
    MIGRATED: hg mv ./devtools/shared/webconsole/test/browser/browser.ini ./devtools/shared/webconsole/test/browser/browser.toml
== 48 of 101 == ./devtools/shared/worker/tests/browser/browser.ini
    Saving INI backup to: ./devtools/shared/worker/tests/browser/browser.ini.bak
    Updating reference in ./devtools/shared/worker/moz.build
    Saving moz.build backup to: ./devtools/shared/worker/moz.build.bak
    MIGRATED: hg mv ./devtools/shared/worker/tests/browser/browser.ini ./devtools/shared/worker/tests/browser/browser.toml
== 49 of 101 == ./devtools/startup/tests/browser/browser.ini
    Saving INI backup to: ./devtools/startup/tests/browser/browser.ini.bak
    Updating reference in ./devtools/startup/moz.build
    Saving moz.build backup to: ./devtools/startup/moz.build.bak
    MIGRATED: hg mv ./devtools/startup/tests/browser/browser.ini ./devtools/startup/tests/browser/browser.toml
== 50 of 101 == ./docshell/test/browser/browser.ini
    Saving INI backup to: ./docshell/test/browser/browser.ini.bak
    Updating reference in ./docshell/moz.build
    Saving moz.build backup to: ./docshell/moz.build.bak
    MIGRATED: hg mv ./docshell/test/browser/browser.ini ./docshell/test/browser/browser.toml
== 51 of 101 == ./docshell/test/navigation/browser.ini
    Saving INI backup to: ./docshell/test/navigation/browser.ini.bak
    Updating reference in ./docshell/moz.build
    MIGRATED: hg mv ./docshell/test/navigation/browser.ini ./docshell/test/navigation/browser.toml
== 52 of 101 == ./dom/base/test/browser.ini
    Saving INI backup to: ./dom/base/test/browser.ini.bak
    Updating reference in ./dom/base/test/moz.build
    Saving moz.build backup to: ./dom/base/test/moz.build.bak
    MIGRATED: hg mv ./dom/base/test/browser.ini ./dom/base/test/browser.toml
== 53 of 101 == ./dom/base/test/fmm/browser.ini
    Saving INI backup to: ./dom/base/test/fmm/browser.ini.bak
    Updating reference in ./dom/base/test/moz.build
    MIGRATED: hg mv ./dom/base/test/fmm/browser.ini ./dom/base/test/fmm/browser.toml
== 54 of 101 == ./dom/base/test/fullscreen/browser.ini
    Saving INI backup to: ./dom/base/test/fullscreen/browser.ini.bak
    Updating reference in ./dom/base/test/fullscreen/moz.build
    Saving moz.build backup to: ./dom/base/test/fullscreen/moz.build.bak
    MIGRATED: hg mv ./dom/base/test/fullscreen/browser.ini ./dom/base/test/fullscreen/browser.toml
== 55 of 101 == ./dom/broadcastchannel/tests/browser.ini
    Saving INI backup to: ./dom/broadcastchannel/tests/browser.ini.bak
    Updating reference in ./dom/broadcastchannel/moz.build
    Saving moz.build backup to: ./dom/broadcastchannel/moz.build.bak
    MIGRATED: hg mv ./dom/broadcastchannel/tests/browser.ini ./dom/broadcastchannel/tests/browser.toml
== 56 of 101 == ./dom/cache/test/browser/browser.ini
    Saving INI backup to: ./dom/cache/test/browser/browser.ini.bak
    Updating reference in ./dom/cache/moz.build
    Saving moz.build backup to: ./dom/cache/moz.build.bak
    MIGRATED: hg mv ./dom/cache/test/browser/browser.ini ./dom/cache/test/browser/browser.toml
== 57 of 101 == ./dom/credentialmanagement/identity/tests/browser/browser.ini
    Saving INI backup to: ./dom/credentialmanagement/identity/tests/browser/browser.ini.bak
    Updating reference in ./dom/credentialmanagement/identity/moz.build
    Saving moz.build backup to: ./dom/credentialmanagement/identity/moz.build.bak
    MIGRATED: hg mv ./dom/credentialmanagement/identity/tests/browser/browser.ini ./dom/credentialmanagement/identity/tests/browser/browser.toml
== 58 of 101 == ./dom/credentialmanagement/tests/browser/browser.ini
    Saving INI backup to: ./dom/credentialmanagement/tests/browser/browser.ini.bak
    Updating reference in ./dom/credentialmanagement/moz.build
    Saving moz.build backup to: ./dom/credentialmanagement/moz.build.bak
    MIGRATED: hg mv ./dom/credentialmanagement/tests/browser/browser.ini ./dom/credentialmanagement/tests/browser/browser.toml
== 59 of 101 == ./dom/crypto/test/browser/browser.ini
    Saving INI backup to: ./dom/crypto/test/browser/browser.ini.bak
    FAILED to write TOML
tmarble@espoir 218 :(
```

By looking at `$MMP/build/convert.err` we see
```
parsing error: No terminal matches '
' in the current parser context, at line 8 col 56

telemetry intermittents, see bug 1539578
                                        ^
```
So disabled needs to be quoted

## run 6

```
tmarble@espoir 219 :) ini2toml $MMP/build/mp-batch6.txt
== 1 of 101 == ./caps/tests/mochitest/browser.ini
    TOML file exists (skipping): ./caps/tests/mochitest/browser.toml
== 2 of 101 == ./devtools/client/aboutdebugging/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/aboutdebugging/test/browser/browser.toml
== 3 of 101 == ./devtools/client/accessibility/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/accessibility/test/browser/browser.toml
== 4 of 101 == ./devtools/client/application/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/application/test/browser/browser.toml
== 5 of 101 == ./devtools/client/debugger/test/mochitest/browser.ini
    TOML file exists (skipping): ./devtools/client/debugger/test/mochitest/browser.toml
== 6 of 101 == ./devtools/client/dom/test/browser.ini
    TOML file exists (skipping): ./devtools/client/dom/test/browser.toml
== 7 of 101 == ./devtools/client/framework/browser-toolbox/test/browser.ini
    TOML file exists (skipping): ./devtools/client/framework/browser-toolbox/test/browser.toml
== 8 of 101 == ./devtools/client/framework/test/browser.ini
    TOML file exists (skipping): ./devtools/client/framework/test/browser.toml
== 9 of 101 == ./devtools/client/inspector/animation/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/animation/test/browser.toml
== 10 of 101 == ./devtools/client/inspector/boxmodel/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/boxmodel/test/browser.toml
== 11 of 101 == ./devtools/client/inspector/changes/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/changes/test/browser.toml
== 12 of 101 == ./devtools/client/inspector/compatibility/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/compatibility/test/browser/browser.toml
== 13 of 101 == ./devtools/client/inspector/computed/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/computed/test/browser.toml
== 14 of 101 == ./devtools/client/inspector/extensions/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/extensions/test/browser.toml
== 15 of 101 == ./devtools/client/inspector/flexbox/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/flexbox/test/browser.toml
== 16 of 101 == ./devtools/client/inspector/fonts/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/fonts/test/browser.toml
== 17 of 101 == ./devtools/client/inspector/grids/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/grids/test/browser.toml
== 18 of 101 == ./devtools/client/inspector/markup/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/markup/test/browser.toml
== 19 of 101 == ./devtools/client/inspector/shared/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/shared/test/browser.toml
== 20 of 101 == ./devtools/client/inspector/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/test/browser.toml
== 21 of 101 == ./devtools/client/jsonview/test/browser.ini
    TOML file exists (skipping): ./devtools/client/jsonview/test/browser.toml
== 22 of 101 == ./devtools/client/memory/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/memory/test/browser/browser.toml
== 23 of 101 == ./devtools/client/netmonitor/src/har/test/browser.ini
    TOML file exists (skipping): ./devtools/client/netmonitor/src/har/test/browser.toml
== 24 of 101 == ./devtools/client/netmonitor/test/browser.ini
    TOML file exists (skipping): ./devtools/client/netmonitor/test/browser.toml
== 25 of 101 == ./devtools/client/performance-new/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/performance-new/test/browser/browser.toml
== 26 of 101 == ./devtools/client/responsive/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/responsive/test/browser/browser.toml
== 27 of 101 == ./devtools/client/shared/components/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/shared/components/test/browser/browser.toml
== 28 of 101 == ./devtools/client/shared/source-map-loader/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/shared/source-map-loader/test/browser/browser.toml
== 29 of 101 == ./devtools/client/shared/sourceeditor/test/browser.ini
    TOML file exists (skipping): ./devtools/client/shared/sourceeditor/test/browser.toml
== 30 of 101 == ./devtools/client/shared/test/browser.ini
    TOML file exists (skipping): ./devtools/client/shared/test/browser.toml
== 31 of 101 == ./devtools/client/storage/test/browser.ini
    TOML file exists (skipping): ./devtools/client/storage/test/browser.toml
== 32 of 101 == ./devtools/client/styleeditor/test/browser.ini
    TOML file exists (skipping): ./devtools/client/styleeditor/test/browser.toml
== 33 of 101 == ./devtools/server/tests/browser/browser.ini
    TOML file exists (skipping): ./devtools/server/tests/browser/browser.toml
== 34 of 101 == ./devtools/server/tracer/tests/browser/browser.ini
    TOML file exists (skipping): ./devtools/server/tracer/tests/browser/browser.toml
== 35 of 101 == ./devtools/shared/commands/inspected-window/tests/browser.ini
    TOML file exists (skipping): ./devtools/shared/commands/inspected-window/tests/browser.toml
== 36 of 101 == ./devtools/shared/commands/inspector/tests/browser.ini
    TOML file exists (skipping): ./devtools/shared/commands/inspector/tests/browser.toml
== 37 of 101 == ./devtools/shared/commands/network/tests/browser.ini
    TOML file exists (skipping): ./devtools/shared/commands/network/tests/browser.toml
== 38 of 101 == ./devtools/shared/commands/resource/tests/browser.ini
    TOML file exists (skipping): ./devtools/shared/commands/resource/tests/browser.toml
== 39 of 101 == ./devtools/shared/commands/script/tests/browser.ini
    TOML file exists (skipping): ./devtools/shared/commands/script/tests/browser.toml
== 40 of 101 == ./devtools/shared/commands/target-configuration/tests/browser.ini
    TOML file exists (skipping): ./devtools/shared/commands/target-configuration/tests/browser.toml
== 41 of 101 == ./devtools/shared/commands/target/tests/browser.ini
    TOML file exists (skipping): ./devtools/shared/commands/target/tests/browser.toml
== 42 of 101 == ./devtools/shared/commands/thread-configuration/tests/browser.ini
    TOML file exists (skipping): ./devtools/shared/commands/thread-configuration/tests/browser.toml
== 43 of 101 == ./devtools/shared/heapsnapshot/tests/browser/browser.ini
    TOML file exists (skipping): ./devtools/shared/heapsnapshot/tests/browser/browser.toml
== 44 of 101 == ./devtools/shared/network-observer/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/shared/network-observer/test/browser/browser.toml
== 45 of 101 == ./devtools/shared/test-helpers/browser.ini
    TOML file exists (skipping): ./devtools/shared/test-helpers/browser.toml
== 46 of 101 == ./devtools/shared/tests/browser/browser.ini
    TOML file exists (skipping): ./devtools/shared/tests/browser/browser.toml
== 47 of 101 == ./devtools/shared/webconsole/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/shared/webconsole/test/browser/browser.toml
== 48 of 101 == ./devtools/shared/worker/tests/browser/browser.ini
    TOML file exists (skipping): ./devtools/shared/worker/tests/browser/browser.toml
== 49 of 101 == ./devtools/startup/tests/browser/browser.ini
    TOML file exists (skipping): ./devtools/startup/tests/browser/browser.toml
== 50 of 101 == ./docshell/test/browser/browser.ini
    TOML file exists (skipping): ./docshell/test/browser/browser.toml
== 51 of 101 == ./docshell/test/navigation/browser.ini
    TOML file exists (skipping): ./docshell/test/navigation/browser.toml
== 52 of 101 == ./dom/base/test/browser.ini
    TOML file exists (skipping): ./dom/base/test/browser.toml
== 53 of 101 == ./dom/base/test/fmm/browser.ini
    TOML file exists (skipping): ./dom/base/test/fmm/browser.toml
== 54 of 101 == ./dom/base/test/fullscreen/browser.ini
    TOML file exists (skipping): ./dom/base/test/fullscreen/browser.toml
== 55 of 101 == ./dom/broadcastchannel/tests/browser.ini
    TOML file exists (skipping): ./dom/broadcastchannel/tests/browser.toml
== 56 of 101 == ./dom/cache/test/browser/browser.ini
    TOML file exists (skipping): ./dom/cache/test/browser/browser.toml
== 57 of 101 == ./dom/credentialmanagement/identity/tests/browser/browser.ini
    TOML file exists (skipping): ./dom/credentialmanagement/identity/tests/browser/browser.toml
== 58 of 101 == ./dom/credentialmanagement/tests/browser/browser.ini
    TOML file exists (skipping): ./dom/credentialmanagement/tests/browser/browser.toml
== 59 of 101 == ./dom/crypto/test/browser/browser.ini
    Updating reference in ./dom/crypto/moz.build
    Saving moz.build backup to: ./dom/crypto/moz.build.bak
    MIGRATED: hg mv ./dom/crypto/test/browser/browser.ini ./dom/crypto/test/browser/browser.toml
== 60 of 101 == ./dom/events/test/browser.ini
    Saving INI backup to: ./dom/events/test/browser.ini.bak
    Updating reference in ./dom/events/moz.build
    Saving moz.build backup to: ./dom/events/moz.build.bak
    MIGRATED: hg mv ./dom/events/test/browser.ini ./dom/events/test/browser.toml
== 61 of 101 == ./dom/events/test/clipboard/browser.ini
    Saving INI backup to: ./dom/events/test/clipboard/browser.ini.bak
    Updating reference in ./dom/events/moz.build
    MIGRATED: hg mv ./dom/events/test/clipboard/browser.ini ./dom/events/test/clipboard/browser.toml
== 62 of 101 == ./dom/fetch/tests/browser.ini
    Saving INI backup to: ./dom/fetch/tests/browser.ini.bak
    Updating reference in ./dom/fetch/moz.build
    Saving moz.build backup to: ./dom/fetch/moz.build.bak
    MIGRATED: hg mv ./dom/fetch/tests/browser.ini ./dom/fetch/tests/browser.toml
== 63 of 101 == ./dom/file/ipc/tests/browser.ini
    Saving INI backup to: ./dom/file/ipc/tests/browser.ini.bak
    Updating reference in ./dom/file/ipc/moz.build
    Saving moz.build backup to: ./dom/file/ipc/moz.build.bak
    MIGRATED: hg mv ./dom/file/ipc/tests/browser.ini ./dom/file/ipc/tests/browser.toml
== 64 of 101 == ./dom/html/test/browser.ini
    Saving INI backup to: ./dom/html/test/browser.ini.bak
    Updating reference in ./dom/html/moz.build
    Saving moz.build backup to: ./dom/html/moz.build.bak
    MIGRATED: hg mv ./dom/html/test/browser.ini ./dom/html/test/browser.toml
== 65 of 101 == ./dom/indexedDB/test/browser.ini
    Saving INI backup to: ./dom/indexedDB/test/browser.ini.bak
    Updating reference in ./dom/indexedDB/moz.build
    Saving moz.build backup to: ./dom/indexedDB/moz.build.bak
    MIGRATED: hg mv ./dom/indexedDB/test/browser.ini ./dom/indexedDB/test/browser.toml
== 66 of 101 == ./dom/ipc/tests/JSProcessActor/browser.ini
    Saving INI backup to: ./dom/ipc/tests/JSProcessActor/browser.ini.bak
    Updating reference in ./dom/ipc/moz.build
    Saving moz.build backup to: ./dom/ipc/moz.build.bak
    MIGRATED: hg mv ./dom/ipc/tests/JSProcessActor/browser.ini ./dom/ipc/tests/JSProcessActor/browser.toml
== 67 of 101 == ./dom/ipc/tests/JSWindowActor/browser.ini
    Saving INI backup to: ./dom/ipc/tests/JSWindowActor/browser.ini.bak
    Updating reference in ./dom/ipc/moz.build
    MIGRATED: hg mv ./dom/ipc/tests/JSWindowActor/browser.ini ./dom/ipc/tests/JSWindowActor/browser.toml
== 68 of 101 == ./dom/ipc/tests/browser.ini
    Saving INI backup to: ./dom/ipc/tests/browser.ini.bak
    Updating reference in ./dom/ipc/moz.build
    MIGRATED: hg mv ./dom/ipc/tests/browser.ini ./dom/ipc/tests/browser.toml
== 69 of 101 == ./dom/l10n/tests/mochitest/browser.ini
    Saving INI backup to: ./dom/l10n/tests/mochitest/browser.ini.bak
    Updating reference in ./dom/l10n/moz.build
    Saving moz.build backup to: ./dom/l10n/moz.build.bak
    MIGRATED: hg mv ./dom/l10n/tests/mochitest/browser.ini ./dom/l10n/tests/mochitest/browser.toml
== 70 of 101 == ./dom/localstorage/test/browser.ini
    Saving INI backup to: ./dom/localstorage/test/browser.ini.bak
    Updating reference in ./dom/localstorage/moz.build
    Saving moz.build backup to: ./dom/localstorage/moz.build.bak
    MIGRATED: hg mv ./dom/localstorage/test/browser.ini ./dom/localstorage/test/browser.toml
== 71 of 101 == ./dom/manifest/test/browser.ini
    Saving INI backup to: ./dom/manifest/test/browser.ini.bak
    Updating reference in ./dom/manifest/moz.build
    Saving moz.build backup to: ./dom/manifest/moz.build.bak
    MIGRATED: hg mv ./dom/manifest/test/browser.ini ./dom/manifest/test/browser.toml
== 72 of 101 == ./dom/media/autoplay/test/browser/browser.ini
    Saving INI backup to: ./dom/media/autoplay/test/browser/browser.ini.bak
    Updating reference in ./dom/media/autoplay/moz.build
    Saving moz.build backup to: ./dom/media/autoplay/moz.build.bak
    MIGRATED: hg mv ./dom/media/autoplay/test/browser/browser.ini ./dom/media/autoplay/test/browser/browser.toml
== 73 of 101 == ./dom/media/doctor/test/browser/browser.ini
    Saving INI backup to: ./dom/media/doctor/test/browser/browser.ini.bak
    Updating reference in ./dom/media/doctor/moz.build
    Saving moz.build backup to: ./dom/media/doctor/moz.build.bak
    MIGRATED: hg mv ./dom/media/doctor/test/browser/browser.ini ./dom/media/doctor/test/browser/browser.toml
== 74 of 101 == ./dom/media/mediacontrol/tests/browser/browser.ini
    Saving INI backup to: ./dom/media/mediacontrol/tests/browser/browser.ini.bak
    Updating reference in ./dom/media/moz.build
    Saving moz.build backup to: ./dom/media/moz.build.bak
    MIGRATED: hg mv ./dom/media/mediacontrol/tests/browser/browser.ini ./dom/media/mediacontrol/tests/browser/browser.toml
== 75 of 101 == ./dom/media/mediasession/test/browser.ini
    Saving INI backup to: ./dom/media/mediasession/test/browser.ini.bak
    Updating reference in ./dom/media/moz.build
    MIGRATED: hg mv ./dom/media/mediasession/test/browser.ini ./dom/media/mediasession/test/browser.toml
== 76 of 101 == ./dom/media/test/browser/browser.ini
    Saving INI backup to: ./dom/media/test/browser/browser.ini.bak
    Updating reference in ./dom/media/moz.build
    MIGRATED: hg mv ./dom/media/test/browser/browser.ini ./dom/media/test/browser/browser.toml
== 77 of 101 == ./dom/media/test/browser/wmfme/browser.ini
    Saving INI backup to: ./dom/media/test/browser/wmfme/browser.ini.bak
    Updating reference in ./dom/media/moz.build
    MIGRATED: hg mv ./dom/media/test/browser/wmfme/browser.ini ./dom/media/test/browser/wmfme/browser.toml
== 78 of 101 == ./dom/midi/tests/browser.ini
    Saving INI backup to: ./dom/midi/tests/browser.ini.bak
    Updating reference in ./dom/midi/moz.build
    Saving moz.build backup to: ./dom/midi/moz.build.bak
    MIGRATED: hg mv ./dom/midi/tests/browser.ini ./dom/midi/tests/browser.toml
== 79 of 101 == ./dom/notification/test/browser/browser.ini
    Saving INI backup to: ./dom/notification/test/browser/browser.ini.bak
    Updating reference in ./dom/notification/moz.build
    Saving moz.build backup to: ./dom/notification/moz.build.bak
    MIGRATED: hg mv ./dom/notification/test/browser/browser.ini ./dom/notification/test/browser/browser.toml
== 80 of 101 == ./dom/payments/test/browser.ini
    Saving INI backup to: ./dom/payments/test/browser.ini.bak
    Updating reference in ./dom/payments/moz.build
    Saving moz.build backup to: ./dom/payments/moz.build.bak
    MIGRATED: hg mv ./dom/payments/test/browser.ini ./dom/payments/test/browser.toml
== 81 of 101 == ./dom/plugins/test/mochitest/browser.ini
    Saving INI backup to: ./dom/plugins/test/mochitest/browser.ini.bak
    Updating reference in ./dom/plugins/test/moz.build
    Saving moz.build backup to: ./dom/plugins/test/moz.build.bak
    MIGRATED: hg mv ./dom/plugins/test/mochitest/browser.ini ./dom/plugins/test/mochitest/browser.toml
== 82 of 101 == ./dom/quota/test/browser/browser.ini
    Saving INI backup to: ./dom/quota/test/browser/browser.ini.bak
    Updating reference in ./dom/quota/test/moz.build
    Saving moz.build backup to: ./dom/quota/test/moz.build.bak
    MIGRATED: hg mv ./dom/quota/test/browser/browser.ini ./dom/quota/test/browser/browser.toml
== 83 of 101 == ./dom/reporting/tests/browser.ini
    Saving INI backup to: ./dom/reporting/tests/browser.ini.bak
    Updating reference in ./dom/reporting/moz.build
    Saving moz.build backup to: ./dom/reporting/moz.build.bak
    MIGRATED: hg mv ./dom/reporting/tests/browser.ini ./dom/reporting/tests/browser.toml
== 84 of 101 == ./dom/security/test/cors/browser.ini
    Saving INI backup to: ./dom/security/test/cors/browser.ini.bak
    Updating reference in ./dom/security/test/moz.build
    Saving moz.build backup to: ./dom/security/test/moz.build.bak
    MIGRATED: hg mv ./dom/security/test/cors/browser.ini ./dom/security/test/cors/browser.toml
== 85 of 101 == ./dom/security/test/csp/browser.ini
    Saving INI backup to: ./dom/security/test/csp/browser.ini.bak
    Updating reference in ./dom/security/test/moz.build
    MIGRATED: hg mv ./dom/security/test/csp/browser.ini ./dom/security/test/csp/browser.toml
== 86 of 101 == ./dom/security/test/general/browser.ini
    Saving INI backup to: ./dom/security/test/general/browser.ini.bak
    WROTE invalid TOML
tmarble@espoir 220 :(
```

By looking at `$MMP/build/sort.err` we see `Error: Unexpected character: 'f' at line 67 col 2`.
That file name was not quoted, so we'll just pre-convert all the support-files.

## run 7

```
tmarble@espoir 221 :) ini2toml $MMP/build/mp-batch6.txt
== 1 of 101 == ./caps/tests/mochitest/browser.ini
    TOML file exists (skipping): ./caps/tests/mochitest/browser.toml
== 2 of 101 == ./devtools/client/aboutdebugging/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/aboutdebugging/test/browser/browser.toml
== 3 of 101 == ./devtools/client/accessibility/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/accessibility/test/browser/browser.toml
== 4 of 101 == ./devtools/client/application/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/application/test/browser/browser.toml
== 5 of 101 == ./devtools/client/debugger/test/mochitest/browser.ini
    TOML file exists (skipping): ./devtools/client/debugger/test/mochitest/browser.toml
== 6 of 101 == ./devtools/client/dom/test/browser.ini
    TOML file exists (skipping): ./devtools/client/dom/test/browser.toml
== 7 of 101 == ./devtools/client/framework/browser-toolbox/test/browser.ini
    TOML file exists (skipping): ./devtools/client/framework/browser-toolbox/test/browser.toml
== 8 of 101 == ./devtools/client/framework/test/browser.ini
    TOML file exists (skipping): ./devtools/client/framework/test/browser.toml
== 9 of 101 == ./devtools/client/inspector/animation/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/animation/test/browser.toml
== 10 of 101 == ./devtools/client/inspector/boxmodel/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/boxmodel/test/browser.toml
== 11 of 101 == ./devtools/client/inspector/changes/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/changes/test/browser.toml
== 12 of 101 == ./devtools/client/inspector/compatibility/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/compatibility/test/browser/browser.toml
== 13 of 101 == ./devtools/client/inspector/computed/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/computed/test/browser.toml
== 14 of 101 == ./devtools/client/inspector/extensions/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/extensions/test/browser.toml
== 15 of 101 == ./devtools/client/inspector/flexbox/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/flexbox/test/browser.toml
== 16 of 101 == ./devtools/client/inspector/fonts/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/fonts/test/browser.toml
== 17 of 101 == ./devtools/client/inspector/grids/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/grids/test/browser.toml
== 18 of 101 == ./devtools/client/inspector/markup/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/markup/test/browser.toml
== 19 of 101 == ./devtools/client/inspector/shared/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/shared/test/browser.toml
== 20 of 101 == ./devtools/client/inspector/test/browser.ini
    TOML file exists (skipping): ./devtools/client/inspector/test/browser.toml
== 21 of 101 == ./devtools/client/jsonview/test/browser.ini
    TOML file exists (skipping): ./devtools/client/jsonview/test/browser.toml
== 22 of 101 == ./devtools/client/memory/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/memory/test/browser/browser.toml
== 23 of 101 == ./devtools/client/netmonitor/src/har/test/browser.ini
    TOML file exists (skipping): ./devtools/client/netmonitor/src/har/test/browser.toml
== 24 of 101 == ./devtools/client/netmonitor/test/browser.ini
    TOML file exists (skipping): ./devtools/client/netmonitor/test/browser.toml
== 25 of 101 == ./devtools/client/performance-new/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/performance-new/test/browser/browser.toml
== 26 of 101 == ./devtools/client/responsive/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/responsive/test/browser/browser.toml
== 27 of 101 == ./devtools/client/shared/components/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/shared/components/test/browser/browser.toml
== 28 of 101 == ./devtools/client/shared/source-map-loader/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/client/shared/source-map-loader/test/browser/browser.toml
== 29 of 101 == ./devtools/client/shared/sourceeditor/test/browser.ini
    TOML file exists (skipping): ./devtools/client/shared/sourceeditor/test/browser.toml
== 30 of 101 == ./devtools/client/shared/test/browser.ini
    TOML file exists (skipping): ./devtools/client/shared/test/browser.toml
== 31 of 101 == ./devtools/client/storage/test/browser.ini
    TOML file exists (skipping): ./devtools/client/storage/test/browser.toml
== 32 of 101 == ./devtools/client/styleeditor/test/browser.ini
    TOML file exists (skipping): ./devtools/client/styleeditor/test/browser.toml
== 33 of 101 == ./devtools/server/tests/browser/browser.ini
    TOML file exists (skipping): ./devtools/server/tests/browser/browser.toml
== 34 of 101 == ./devtools/server/tracer/tests/browser/browser.ini
    TOML file exists (skipping): ./devtools/server/tracer/tests/browser/browser.toml
== 35 of 101 == ./devtools/shared/commands/inspected-window/tests/browser.ini
    TOML file exists (skipping): ./devtools/shared/commands/inspected-window/tests/browser.toml
== 36 of 101 == ./devtools/shared/commands/inspector/tests/browser.ini
    TOML file exists (skipping): ./devtools/shared/commands/inspector/tests/browser.toml
== 37 of 101 == ./devtools/shared/commands/network/tests/browser.ini
    TOML file exists (skipping): ./devtools/shared/commands/network/tests/browser.toml
== 38 of 101 == ./devtools/shared/commands/resource/tests/browser.ini
    TOML file exists (skipping): ./devtools/shared/commands/resource/tests/browser.toml
== 39 of 101 == ./devtools/shared/commands/script/tests/browser.ini
    TOML file exists (skipping): ./devtools/shared/commands/script/tests/browser.toml
== 40 of 101 == ./devtools/shared/commands/target-configuration/tests/browser.ini
    TOML file exists (skipping): ./devtools/shared/commands/target-configuration/tests/browser.toml
== 41 of 101 == ./devtools/shared/commands/target/tests/browser.ini
    TOML file exists (skipping): ./devtools/shared/commands/target/tests/browser.toml
== 42 of 101 == ./devtools/shared/commands/thread-configuration/tests/browser.ini
    TOML file exists (skipping): ./devtools/shared/commands/thread-configuration/tests/browser.toml
== 43 of 101 == ./devtools/shared/heapsnapshot/tests/browser/browser.ini
    TOML file exists (skipping): ./devtools/shared/heapsnapshot/tests/browser/browser.toml
== 44 of 101 == ./devtools/shared/network-observer/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/shared/network-observer/test/browser/browser.toml
== 45 of 101 == ./devtools/shared/test-helpers/browser.ini
    TOML file exists (skipping): ./devtools/shared/test-helpers/browser.toml
== 46 of 101 == ./devtools/shared/tests/browser/browser.ini
    TOML file exists (skipping): ./devtools/shared/tests/browser/browser.toml
== 47 of 101 == ./devtools/shared/webconsole/test/browser/browser.ini
    TOML file exists (skipping): ./devtools/shared/webconsole/test/browser/browser.toml
== 48 of 101 == ./devtools/shared/worker/tests/browser/browser.ini
    TOML file exists (skipping): ./devtools/shared/worker/tests/browser/browser.toml
== 49 of 101 == ./devtools/startup/tests/browser/browser.ini
    TOML file exists (skipping): ./devtools/startup/tests/browser/browser.toml
== 50 of 101 == ./docshell/test/browser/browser.ini
    TOML file exists (skipping): ./docshell/test/browser/browser.toml
== 51 of 101 == ./docshell/test/navigation/browser.ini
    TOML file exists (skipping): ./docshell/test/navigation/browser.toml
== 52 of 101 == ./dom/base/test/browser.ini
    TOML file exists (skipping): ./dom/base/test/browser.toml
== 53 of 101 == ./dom/base/test/fmm/browser.ini
    TOML file exists (skipping): ./dom/base/test/fmm/browser.toml
== 54 of 101 == ./dom/base/test/fullscreen/browser.ini
    TOML file exists (skipping): ./dom/base/test/fullscreen/browser.toml
== 55 of 101 == ./dom/broadcastchannel/tests/browser.ini
    TOML file exists (skipping): ./dom/broadcastchannel/tests/browser.toml
== 56 of 101 == ./dom/cache/test/browser/browser.ini
    TOML file exists (skipping): ./dom/cache/test/browser/browser.toml
== 57 of 101 == ./dom/credentialmanagement/identity/tests/browser/browser.ini
    TOML file exists (skipping): ./dom/credentialmanagement/identity/tests/browser/browser.toml
== 58 of 101 == ./dom/credentialmanagement/tests/browser/browser.ini
    TOML file exists (skipping): ./dom/credentialmanagement/tests/browser/browser.toml
== 59 of 101 == ./dom/crypto/test/browser/browser.ini
    TOML file exists (skipping): ./dom/crypto/test/browser/browser.toml
== 60 of 101 == ./dom/events/test/browser.ini
    TOML file exists (skipping): ./dom/events/test/browser.toml
== 61 of 101 == ./dom/events/test/clipboard/browser.ini
    TOML file exists (skipping): ./dom/events/test/clipboard/browser.toml
== 62 of 101 == ./dom/fetch/tests/browser.ini
    TOML file exists (skipping): ./dom/fetch/tests/browser.toml
== 63 of 101 == ./dom/file/ipc/tests/browser.ini
    TOML file exists (skipping): ./dom/file/ipc/tests/browser.toml
== 64 of 101 == ./dom/html/test/browser.ini
    TOML file exists (skipping): ./dom/html/test/browser.toml
== 65 of 101 == ./dom/indexedDB/test/browser.ini
    TOML file exists (skipping): ./dom/indexedDB/test/browser.toml
== 66 of 101 == ./dom/ipc/tests/JSProcessActor/browser.ini
    TOML file exists (skipping): ./dom/ipc/tests/JSProcessActor/browser.toml
== 67 of 101 == ./dom/ipc/tests/JSWindowActor/browser.ini
    TOML file exists (skipping): ./dom/ipc/tests/JSWindowActor/browser.toml
== 68 of 101 == ./dom/ipc/tests/browser.ini
    TOML file exists (skipping): ./dom/ipc/tests/browser.toml
== 69 of 101 == ./dom/l10n/tests/mochitest/browser.ini
    TOML file exists (skipping): ./dom/l10n/tests/mochitest/browser.toml
== 70 of 101 == ./dom/localstorage/test/browser.ini
    TOML file exists (skipping): ./dom/localstorage/test/browser.toml
== 71 of 101 == ./dom/manifest/test/browser.ini
    TOML file exists (skipping): ./dom/manifest/test/browser.toml
== 72 of 101 == ./dom/media/autoplay/test/browser/browser.ini
    TOML file exists (skipping): ./dom/media/autoplay/test/browser/browser.toml
== 73 of 101 == ./dom/media/doctor/test/browser/browser.ini
    TOML file exists (skipping): ./dom/media/doctor/test/browser/browser.toml
== 74 of 101 == ./dom/media/mediacontrol/tests/browser/browser.ini
    TOML file exists (skipping): ./dom/media/mediacontrol/tests/browser/browser.toml
== 75 of 101 == ./dom/media/mediasession/test/browser.ini
    TOML file exists (skipping): ./dom/media/mediasession/test/browser.toml
== 76 of 101 == ./dom/media/test/browser/browser.ini
    TOML file exists (skipping): ./dom/media/test/browser/browser.toml
== 77 of 101 == ./dom/media/test/browser/wmfme/browser.ini
    TOML file exists (skipping): ./dom/media/test/browser/wmfme/browser.toml
== 78 of 101 == ./dom/midi/tests/browser.ini
    TOML file exists (skipping): ./dom/midi/tests/browser.toml
== 79 of 101 == ./dom/notification/test/browser/browser.ini
    TOML file exists (skipping): ./dom/notification/test/browser/browser.toml
== 80 of 101 == ./dom/payments/test/browser.ini
    TOML file exists (skipping): ./dom/payments/test/browser.toml
== 81 of 101 == ./dom/plugins/test/mochitest/browser.ini
    TOML file exists (skipping): ./dom/plugins/test/mochitest/browser.toml
== 82 of 101 == ./dom/quota/test/browser/browser.ini
    TOML file exists (skipping): ./dom/quota/test/browser/browser.toml
== 83 of 101 == ./dom/reporting/tests/browser.ini
    TOML file exists (skipping): ./dom/reporting/tests/browser.toml
== 84 of 101 == ./dom/security/test/cors/browser.ini
    TOML file exists (skipping): ./dom/security/test/cors/browser.toml
== 85 of 101 == ./dom/security/test/csp/browser.ini
    TOML file exists (skipping): ./dom/security/test/csp/browser.toml
== 86 of 101 == ./dom/security/test/general/browser.ini
    Updating reference in ./dom/security/test/moz.build
    MIGRATED: hg mv ./dom/security/test/general/browser.ini ./dom/security/test/general/browser.toml
== 87 of 101 == ./dom/security/test/https-first/browser.ini
    Saving INI backup to: ./dom/security/test/https-first/browser.ini.bak
    Updating reference in ./dom/security/test/moz.build
    MIGRATED: hg mv ./dom/security/test/https-first/browser.ini ./dom/security/test/https-first/browser.toml
== 88 of 101 == ./dom/security/test/https-only/browser.ini
    Saving INI backup to: ./dom/security/test/https-only/browser.ini.bak
    Updating reference in ./dom/security/test/moz.build
    MIGRATED: hg mv ./dom/security/test/https-only/browser.ini ./dom/security/test/https-only/browser.toml
== 89 of 101 == ./dom/security/test/mixedcontentblocker/browser.ini
    Saving INI backup to: ./dom/security/test/mixedcontentblocker/browser.ini.bak
    Updating reference in ./dom/security/test/moz.build
    MIGRATED: hg mv ./dom/security/test/mixedcontentblocker/browser.ini ./dom/security/test/mixedcontentblocker/browser.toml
== 90 of 101 == ./dom/security/test/referrer-policy/browser.ini
    Saving INI backup to: ./dom/security/test/referrer-policy/browser.ini.bak
    Updating reference in ./dom/security/test/moz.build
    MIGRATED: hg mv ./dom/security/test/referrer-policy/browser.ini ./dom/security/test/referrer-policy/browser.toml
== 91 of 101 == ./dom/security/test/sec-fetch/browser.ini
    Saving INI backup to: ./dom/security/test/sec-fetch/browser.ini.bak
    Updating reference in ./dom/security/test/moz.build
    MIGRATED: hg mv ./dom/security/test/sec-fetch/browser.ini ./dom/security/test/sec-fetch/browser.toml
== 92 of 101 == ./dom/serviceworkers/test/browser-common.ini
    Saving INI backup to: ./dom/serviceworkers/test/browser-common.ini.bak
    MIGRATED: hg mv ./dom/serviceworkers/test/browser-common.ini ./dom/serviceworkers/test/browser-common.toml
== 93 of 101 == ./dom/serviceworkers/test/browser-dFPI.ini
    Saving INI backup to: ./dom/serviceworkers/test/browser-dFPI.ini.bak
    Updating reference in ./dom/serviceworkers/moz.build
    Saving moz.build backup to: ./dom/serviceworkers/moz.build.bak
    MIGRATED: hg mv ./dom/serviceworkers/test/browser-dFPI.ini ./dom/serviceworkers/test/browser-dFPI.toml
== 94 of 101 == ./dom/serviceworkers/test/browser.ini
    Saving INI backup to: ./dom/serviceworkers/test/browser.ini.bak
    Updating reference in ./dom/serviceworkers/moz.build
    MIGRATED: hg mv ./dom/serviceworkers/test/browser.ini ./dom/serviceworkers/test/browser.toml
== 95 of 101 == ./dom/serviceworkers/test/isolated/multi-e10s-update/browser.ini
    Saving INI backup to: ./dom/serviceworkers/test/isolated/multi-e10s-update/browser.ini.bak
    Updating reference in ./dom/serviceworkers/moz.build
    MIGRATED: hg mv ./dom/serviceworkers/test/isolated/multi-e10s-update/browser.ini ./dom/serviceworkers/test/isolated/multi-e10s-update/browser.toml
== 96 of 101 == ./dom/tests/browser/browser.ini
    Saving INI backup to: ./dom/tests/browser/browser.ini.bak
    Updating reference in ./dom/tests/moz.build
    Saving moz.build backup to: ./dom/tests/moz.build.bak
    MIGRATED: hg mv ./dom/tests/browser/browser.ini ./dom/tests/browser/browser.toml
== 97 of 101 == ./dom/url/tests/browser.ini
    Saving INI backup to: ./dom/url/tests/browser.ini.bak
    Updating reference in ./dom/url/moz.build
    Saving moz.build backup to: ./dom/url/moz.build.bak
    MIGRATED: hg mv ./dom/url/tests/browser.ini ./dom/url/tests/browser.toml
== 98 of 101 == ./dom/webauthn/tests/browser/browser.ini
    Saving INI backup to: ./dom/webauthn/tests/browser/browser.ini.bak
    Updating reference in ./dom/webauthn/moz.build
    Saving moz.build backup to: ./dom/webauthn/moz.build.bak
    MIGRATED: hg mv ./dom/webauthn/tests/browser/browser.ini ./dom/webauthn/tests/browser/browser.toml
== 99 of 101 == ./dom/workers/test/browser.ini
    Saving INI backup to: ./dom/workers/test/browser.ini.bak
    Updating reference in ./dom/workers/moz.build
    Saving moz.build backup to: ./dom/workers/moz.build.bak
    MIGRATED: hg mv ./dom/workers/test/browser.ini ./dom/workers/test/browser.toml
== 100 of 101 == ./dom/xhr/tests/browser.ini
    Saving INI backup to: ./dom/xhr/tests/browser.ini.bak
    Updating reference in ./dom/xhr/moz.build
    Saving moz.build backup to: ./dom/xhr/moz.build.bak
    MIGRATED: hg mv ./dom/xhr/tests/browser.ini ./dom/xhr/tests/browser.toml
== 101 of 101 == ./dom/xslt/tests/browser/browser.ini
    Saving INI backup to: ./dom/xslt/tests/browser/browser.ini.bak
    Updating reference in ./dom/xslt/moz.build
    Saving moz.build backup to: ./dom/xslt/moz.build.bak
    MIGRATED: hg mv ./dom/xslt/tests/browser/browser.ini ./dom/xslt/tests/browser/browser.toml
Updated ./caps/moz.build
Updated ./devtools/client/aboutdebugging/moz.build
Updated ./devtools/client/accessibility/moz.build
Updated ./devtools/client/application/moz.build
Updated ./devtools/client/debugger/moz.build
Updated ./devtools/client/dom/moz.build
Updated ./devtools/client/framework/browser-toolbox/moz.build
Updated ./devtools/client/framework/moz.build
Updated ./devtools/client/inspector/animation/moz.build
Updated ./devtools/client/inspector/boxmodel/moz.build
Updated ./devtools/client/inspector/changes/moz.build
Updated ./devtools/client/inspector/compatibility/moz.build
Updated ./devtools/client/inspector/computed/moz.build
Updated ./devtools/client/inspector/extensions/moz.build
Updated ./devtools/client/inspector/flexbox/moz.build
Updated ./devtools/client/inspector/fonts/moz.build
Updated ./devtools/client/inspector/grids/moz.build
Updated ./devtools/client/inspector/markup/moz.build
Updated ./devtools/client/inspector/shared/moz.build
Updated ./devtools/client/inspector/moz.build
Updated ./devtools/client/jsonview/moz.build
Updated ./devtools/client/memory/moz.build
Updated ./devtools/client/netmonitor/src/har/moz.build
Updated ./devtools/client/netmonitor/moz.build
Updated ./devtools/client/performance-new/moz.build
Updated ./devtools/client/responsive/moz.build
Updated ./devtools/client/shared/components/moz.build
Updated ./devtools/client/shared/source-map-loader/moz.build
Updated ./devtools/client/shared/sourceeditor/moz.build
Updated ./devtools/client/shared/moz.build
Updated ./devtools/client/storage/moz.build
Updated ./devtools/client/styleeditor/moz.build
Updated ./devtools/server/moz.build
Updated ./devtools/server/tracer/moz.build
Updated ./devtools/shared/commands/inspected-window/moz.build
Updated ./devtools/shared/commands/inspector/moz.build
Updated ./devtools/shared/commands/network/moz.build
Updated ./devtools/shared/commands/resource/moz.build
Updated ./devtools/shared/commands/script/moz.build
Updated ./devtools/shared/commands/target-configuration/moz.build
Updated ./devtools/shared/commands/target/moz.build
Updated ./devtools/shared/heapsnapshot/moz.build
Updated ./devtools/shared/network-observer/moz.build
Updated ./devtools/shared/moz.build
Updated ./devtools/shared/webconsole/moz.build
Updated ./devtools/shared/worker/moz.build
Updated ./devtools/startup/moz.build
Updated ./docshell/moz.build
Updated ./dom/base/test/moz.build
Updated ./dom/base/test/fullscreen/moz.build
Updated ./dom/broadcastchannel/moz.build
Updated ./dom/cache/moz.build
Updated ./dom/credentialmanagement/identity/moz.build
Updated ./dom/credentialmanagement/moz.build
Updated ./dom/crypto/moz.build
Updated ./dom/events/moz.build
Updated ./dom/fetch/moz.build
Updated ./dom/file/ipc/moz.build
Updated ./dom/html/moz.build
Updated ./dom/indexedDB/moz.build
Updated ./dom/ipc/moz.build
Updated ./dom/l10n/moz.build
Updated ./dom/localstorage/moz.build
Updated ./dom/manifest/moz.build
Updated ./dom/media/autoplay/moz.build
Updated ./dom/media/doctor/moz.build
Updated ./dom/media/moz.build
Updated ./dom/midi/moz.build
Updated ./dom/notification/moz.build
Updated ./dom/payments/moz.build
Updated ./dom/plugins/test/moz.build
Updated ./dom/quota/test/moz.build
Updated ./dom/reporting/moz.build
Updated ./dom/security/test/moz.build
Updated ./dom/serviceworkers/moz.build
Updated ./dom/tests/moz.build
Updated ./dom/url/moz.build
Updated ./dom/webauthn/moz.build
Updated ./dom/workers/moz.build
Updated ./dom/xhr/moz.build
Updated ./dom/xslt/moz.build
tmarble@espoir 222 :)
```

## Manual TOML review

As certain transformations to our target ManifestParser TOML style
are difficult to automate each TOML file will be reviewed manually
to ensure it matches our style guide in [LINTER](LINTER.md).

One approach to performing this manual review is to loop through the
INI files being migrated and compare the original INI and resulting
TOML side by side in a text editor. Here is an example using Emacs
which will open both the INI file (`*.ini.bak`) and the TOML file.
Typically small changes within the INI file will allow the migration to proceed

```
for ini in $(cat $MMP/build/mp-batch6.txt); do \
  echo == $ini ==;  \
  toml=${ini%%.ini}.toml; \
  emacsclient -n $ini.bak; \
  emacsclient $toml; \
done
```

## Lint TOML

Once all the TOML files have been reviewed it's worth a quick check
to validate that they are still legal TOML. It is very easy to misplace
a quote or a comma and causing parsing to fail. The `read-toml.py` program
will parse the TOML file using **tomlkit** and flag any errors.

```
for ini in $(cat $MMP/build/mp-batch6.txt); do \
  echo == $ini ==;  \
  toml=${ini%%.ini}.toml; \
  $MMP/read-toml.py -r $toml > /dev/null; \
done
```

## Lint moz.build

The **ini2toml** program modified the `moz.build` files and those need
to be checked by the **black** linter to ensure they continue to match
expected syntax.

```
./mach lint --verbose --fix --warnings --linter black $(cat $MMP/build/mbfiles.txt)
```

## commit

Once the linters have completed successfully then the changeset can be committed.
Note that `hg status` will show the `*.bak` files as new/unknown -- we can
delete these later.

```
hg commit -m "Bug 1853244 - convert .ini manifests to .toml: batch 6 {caps,devtools,dom}/**/browser.ini r=jmaher"
```


## try

For these `browser.ini` files the appropriate **try** commands are:

```
./mach try fuzzy -q 'mochitest devtools'
./mach try fuzzy -q 'mochitest-browser-chrome'
```
## moz phab

Once the **try** is successful then we can submit a review:

```
moz-phab submit .
```
## answer review questions

Reviewers will likely have questions that need to be resolved

## Lando

Once the review is complete the changeset can be lando'd.

## cleanup

Now that the changeset has been complete our temporary `*.bak` files can
be deleted.

Verify the files to be deleted with:

```
find . -name '*.bak'
```

If the list of files looks accurate, you may proceed to delete them with:

```
find . -name '*.bak' | xargs rm
```
