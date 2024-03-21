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

package com.gerritforge.ghs.gerrit.uploadpackmetrics;

import com.google.common.flogger.FluentLogger;
import com.google.gerrit.extensions.annotations.PluginName;
import com.google.gerrit.metrics.Description;
import com.google.gerrit.metrics.Description.Units;
import com.google.gerrit.metrics.MetricMaker;
import com.google.gerrit.server.config.PluginConfigFactory;
import com.google.inject.Inject;
import com.google.inject.Singleton;
import java.util.concurrent.atomic.AtomicReference;
import java.util.regex.Pattern;
import org.eclipse.jgit.storage.pack.PackStatistics;
import org.eclipse.jgit.transport.PostUploadHook;

@Singleton
class UploadPackPerRepoMetrics implements PostUploadHook {
  private static final String UPLOAD_PACK_METRICS_REPO = "uploadPackMetricsRepo";
  private static final FluentLogger log = FluentLogger.forEnclosingClass();

  private final String repoName;
  private final AtomicReference<PackStatistics> lastStats = new AtomicReference<>();
  private final Pattern repoNamePattern;
  private final UploadPackMetricsLogger uploadpackMetricsLogger;

  @Inject
  UploadPackPerRepoMetrics(
      MetricMaker metricMaker,
      PluginConfigFactory cfgFactory,
      @PluginName String pluginName,
      UploadPackMetricsLogger uploadPackMetricsLogger) {
    this.repoName = cfgFactory.getFromGerritConfig(pluginName).getString(UPLOAD_PACK_METRICS_REPO);
    log.atInfo().log("Installing metrics for %s", repoName);

    this.repoNamePattern =
        Pattern.compile(String.format(" (/a)?/%s(/git-upload-pack| )", repoName));
    this.uploadpackMetricsLogger = uploadPackMetricsLogger;

    metricMaker.newCallbackMetric(
        String.format("ghs/git-upload-pack/bitmap_index_misses/%s", repoName),
        Long.class,
        new Description(String.format("Bitmap index misses for repo %s", repoName))
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

    metricMaker.newCallbackMetric(
        String.format("ghs/git-upload-pack/phase_searching_for_reuse/%s", repoName),
        Long.class,
        new Description(
                String.format(
                    "time jgit searched for deltas which can be reused for repo %s", repoName))
            .setGauge()
            .setUnit(Units.MILLISECONDS),
        () -> {
          PackStatistics packStatistics = lastStats.get();
          long timeSearchingForReuse = -1;
          if (packStatistics != null) {
            timeSearchingForReuse = packStatistics.getTimeSearchingForReuse();
          }
          return timeSearchingForReuse;
        });
  }

  @Override
  public void onPostUpload(PackStatistics stats) {
    if (repoNamePattern.matcher(Thread.currentThread().getName()).find()) {
      logStats(stats);
      lastStats.set(stats);
    }
  }

  private void logStats(PackStatistics stats) {
    uploadpackMetricsLogger.log(repoName, stats);
  }
}
