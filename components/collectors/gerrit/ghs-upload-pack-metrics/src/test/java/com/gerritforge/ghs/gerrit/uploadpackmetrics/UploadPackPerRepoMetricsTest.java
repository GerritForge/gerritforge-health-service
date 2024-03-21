package com.gerritforge.ghs.gerrit.uploadpackmetrics;

import com.google.gerrit.metrics.DisabledMetricMaker;
import org.junit.Test;
import static com.google.common.truth.Truth.assertThat;

import java.nio.file.Path;

public class UploadPackPerRepoMetricsTest {

  @Test
  public void shouldCreateLogFileWithMetrics (){
    new UploadPackPerRepoMetrics(new DisabledMetricMaker(), "testProject", "testPlugin" );


    assertThat(Path.of("/test/folder").toFile().exists()).isTrue();
  }
}
