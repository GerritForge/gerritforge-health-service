package com.gerritforge.ghs.gerrit.uploadpackmetrics;

import com.google.gerrit.acceptance.LightweightPluginDaemonTest;
import com.google.gerrit.acceptance.TestPlugin;
import com.google.gerrit.acceptance.UseLocalDisk;
import org.junit.Test;

import static com.google.common.truth.Truth.assertThat;

import java.io.File;
import java.nio.file.Path;

@TestPlugin(
    name = "ghs-upload-pack-metrics",
    sysModule = "com.gerritforge.ghs.gerrit.uploadpackmetrics.Module")
public class UploadPackPerRepoMetricsTest extends LightweightPluginDaemonTest {
  @Test
  @UseLocalDisk
  public void shouldCreateLogFileWithMetrics () {
    String logsFolder = null;
    for (File file : new File(temporaryFolder.getRoot().getAbsolutePath()).listFiles()) {
      if(file.isDirectory()) {
         logsFolder = file.getAbsolutePath() + "/logs";
      }
    }
    assertThat(Path.of(logsFolder + "/upload_pack_metrics_log").toFile().exists()).isTrue();
  }
}
