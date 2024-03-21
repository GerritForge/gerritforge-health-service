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

import com.google.gerrit.extensions.systemstatus.ServerInformation;
import com.google.gerrit.server.util.PluginLogFile;
import com.google.gerrit.server.util.SystemLog;
import com.google.inject.Inject;
import org.apache.log4j.PatternLayout;
import org.eclipse.jgit.storage.pack.PackStatistics;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class UploadPackMetricsLogger extends PluginLogFile {
  static final String UPLOAD_PACK_METRICS_LOG_NAME = "upload_pack_metrics_log";

  private final Logger uploadPackMetricsLogger;

  @Inject
  UploadPackMetricsLogger(SystemLog systemLog, ServerInformation serverInfo) {
    super(systemLog, serverInfo, UPLOAD_PACK_METRICS_LOG_NAME, new PatternLayout("[%d] %m%n"));
    this.uploadPackMetricsLogger = LoggerFactory.getLogger(UPLOAD_PACK_METRICS_LOG_NAME);
  }

  void log(String repoName, PackStatistics stats) {
    uploadPackMetricsLogger.info(
        "{} {} {}", repoName, stats.getTimeSearchingForReuse(), stats.getBitmapIndexMisses());
  }
}
