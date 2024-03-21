package com.gerritforge.ghs.gerrit.uploadpackmetrics;

import com.google.gerrit.extensions.systemstatus.ServerInformation;
import com.google.gerrit.server.util.PluginLogFile;
import com.google.gerrit.server.util.SystemLog;
import com.google.inject.Inject;
import org.apache.log4j.PatternLayout;
import org.eclipse.jgit.storage.pack.PackStatistics;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class UploadPackMetricsLogger extends PluginLogFile {

  public static final String UPLOAD_PACK_METRICS_LOG_NAME = "upload_pack_metrics_log";

  public final Logger uploadPackMetricsLogger;

  @Inject
  public UploadPackMetricsLogger(SystemLog systemLog, ServerInformation serverInfo) {
    super(
        systemLog,
        serverInfo,
        UPLOAD_PACK_METRICS_LOG_NAME,
        new PatternLayout("[%d] %m%n")
    );
    this.uploadPackMetricsLogger = LoggerFactory.getLogger(UPLOAD_PACK_METRICS_LOG_NAME);
  }

  public void log(String repoName, PackStatistics stats) {
    uploadPackMetricsLogger.info("{} {} {}", repoName, stats.getTimeSearchingForReuse(), stats.getBitmapIndexMisses());
  }
}
