### Metrics Logs

Metrics are also logged to `$site_path/logs/upload_pack_metrics_log`.


#### Time Format

For all timestamps the format [dd MMM yyyy HH:mm:ss,SSS] is used. This format is both ISO 8601 and RFC3339 compatible.

#### Field Order

The following format is observed:

- repoName - Name of the repository for which that metric is bein registered.
- timeSearchingForReuse - Get time in milliseconds spent matching existing representations against objects that will be transmitted.
- bitmapIndexMisses - Get the count of objects that needed to be discovered through an object walk because they were not found in bitmap indices.
