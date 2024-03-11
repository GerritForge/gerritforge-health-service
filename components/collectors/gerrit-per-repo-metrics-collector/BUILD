load("//tools/bzl:plugin.bzl", "gerrit_plugin")

gerrit_plugin(
    name = "gerrit-per-repo-metrics-collector",
    srcs = glob(["src/main/java/**/*.java"]),
    manifest_entries = [
        "Gerrit-PluginName: gerrit-per-repo-metrics-collector",
        "Gerrit-Module: com.googlesource.gerrit.plugins.perrepo.metricscollector.Module",
    ],
    resources = glob(["src/main/resources/**/*"]),
)
