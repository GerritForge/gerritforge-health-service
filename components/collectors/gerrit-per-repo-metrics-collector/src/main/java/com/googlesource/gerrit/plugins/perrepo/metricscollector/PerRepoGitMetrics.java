// Copyright (C) 2024 GerritForge, Inc.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package com.googlesource.gerrit.plugins.perrepo.metricscollector;

import com.google.gerrit.extensions.annotations.PluginName;
import com.google.gerrit.metrics.Description;
import com.google.gerrit.metrics.MetricMaker;
import com.google.gerrit.server.config.PluginConfigFactory;
import com.google.inject.Inject;
import com.google.inject.Singleton;
import java.util.concurrent.atomic.AtomicReference;
import org.eclipse.jgit.storage.pack.PackStatistics;
import org.eclipse.jgit.transport.PostUploadHook;

@Singleton
public class PerRepoGitMetrics implements PostUploadHook {
  private static final String UPLOAD_PACK_METRICS_REPO = "uploadPackMetricsRepo";
  private final AtomicReference<PackStatistics> lastStats = new AtomicReference<>();
  private final String configRepoName;

  @Inject
  public PerRepoGitMetrics(
      MetricMaker metricMaker, PluginConfigFactory cfgFactory, @PluginName String pluginName) {
    configRepoName = cfgFactory.getFromGerritConfig(pluginName).getString(UPLOAD_PACK_METRICS_REPO);
    metricMaker.newCallbackMetric(
        String.format("git/upload-pack/bitmap_index_misses/%s", configRepoName),
        Long.class,
        new Description(String.format("Bitmap index misses for repo %s", configRepoName))
            .setGauge()
            .setUnit("misses"),
        () -> {
          PackStatistics packStatistics = lastStats.get();
          long bitmapIndexMisses = 0;
          if (packStatistics != null) {
            bitmapIndexMisses = packStatistics.getBitmapIndexMisses();
          }
          return bitmapIndexMisses;
        });
  }

  @Override
  public void onPostUpload(PackStatistics stats) {
    if (Thread.currentThread().getName().contains(configRepoName)) {
      lastStats.set(stats);
    }
  }
}
