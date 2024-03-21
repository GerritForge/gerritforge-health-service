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

junit_tests(
    name = "ghs-upload-pack-metrics_tests",
    srcs = glob(
        [
            "src/test/java/**/*Test.java",
        ],
    ),
    resources = glob(["src/test/resources/**/*"]),
    deps = PLUGIN_DEPS + PLUGIN_TEST_DEPS + [
        ":ghs-upload-pack-metrics__plugin",
    ],
)
