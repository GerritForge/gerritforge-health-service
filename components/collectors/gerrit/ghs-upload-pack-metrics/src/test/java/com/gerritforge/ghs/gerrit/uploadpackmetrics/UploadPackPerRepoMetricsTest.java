package com.gerritforge.ghs.gerrit.uploadpackmetrics;

import com.google.gerrit.metrics.DisabledMetricMaker;
import com.google.gerrit.metrics.MetricMaker;
import org.eclipse.jgit.storage.pack.PackStatistics;
import org.junit.Test;
import static com.google.common.truth.Truth.assertThat;

import java.nio.file.Path;

public class UploadPackPerRepoMetricsTest {

  @Test
  public void shouldCreateLogFileWithMetrics (){
    String projectName = "testProject";
    FakeUploadPackPerRepoMetrics fakeUploadPackPerRepoMetrics =
        new FakeUploadPackPerRepoMetrics(new DisabledMetricMaker(), projectName, "testPlugin");

    PackStatistics.Accumulator stats = new PackStatistics.Accumulator();
    stats.advertised += 10;
    stats.bitmapIndexMisses += 3;
    stats.timeNegotiating += 5;
    PackStatistics packStats = new PackStatistics(stats);
    Thread.currentThread().setName(String.format(" /a/%s/git-upload-pack", projectName));
    fakeUploadPackPerRepoMetrics.onPostUpload(packStats);

    assertThat(Path.of("/tmp/test/folder/stats.txt").toFile().exists()).isTrue();
  }

  private static final class FakeUploadPackPerRepoMetrics extends UploadPackPerRepoMetrics {
    FakeUploadPackPerRepoMetrics(MetricMaker metricMaker, String configRepoName, String pluginName) {
      super(metricMaker, configRepoName, pluginName);
    }
  }
}
