Build
=====

With Bazel
----------

This plugin can be built with Bazel.

Clone (or link) this plugin to the `plugins` directory of Gerrit's source tree.
Put the external dependency Bazel build file into the Gerrit /plugins directory,
replacing the existing empty one.

```
  bazel build plugins/@PLUGIN@
```

in the root of Gerrit's source tree to build
The output is created in

```
  bazel-bin/plugins/@PLUGIN@/@PLUGIN@.jar
```
