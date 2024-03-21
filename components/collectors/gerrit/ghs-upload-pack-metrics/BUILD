load("//tools/bzl:plugin.bzl", "gerrit_plugin")

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
