package com.gerritforge.ghs.gerrit.uploadpackmetrics;

import com.google.gerrit.extensions.systemstatus.ServerInformation;
import com.google.gerrit.server.util.PluginLogFile;
import com.google.gerrit.server.util.SystemLog;
import com.google.inject.Inject;
import org.apache.log4j.PatternLayout;

public class UploadPackMetricsLogFile extends PluginLogFile {

@Inject
  public UploadPackMetricsLogFile(SystemLog systemLog, ServerInformation serverInfo) {
    super(
        systemLog,
        serverInfo,
        UploadPackMetricsLogger.UPLOAD_PACK_METRICS_LOG_NAME,
        new PatternLayout("[%d %m%n]")
    );
  }
}
