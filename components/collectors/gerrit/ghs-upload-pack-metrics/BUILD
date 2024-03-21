load("//tools/bzl:junit.bzl", "junit_tests")
load(
    "//tools/bzl:plugin.bzl",
    "PLUGIN_DEPS",
    "PLUGIN_TEST_DEPS",
    "gerrit_plugin",
)

gerrit_plugin(
    name = "ghs-upload-pack-metrics",
    srcs = glob(["src/main/java/**/*.java"]),
    manifest_entries = [
        "Gerrit-PluginName: ghs-upload-pack-metrics",
        "Gerrit-Module: com.gerritforge.ghs.gerrit.uploadpackmetrics.Module",
        "Gerrit-ReloadMode: restart",
    ],
    resources = glob(["src/main/resources/**/*"]),
)

[junit_tests(
    name = f[:f.index(".")].replace("/", "_"),
    srcs = [f],
    tags = ["ghs-upload-pack-metrics"],
    deps = PLUGIN_DEPS + PLUGIN_TEST_DEPS + [
        ":ghs-upload-pack-metrics__plugin",
    ],
) for f in glob(["src/test/java/**/*IT.java"])]
