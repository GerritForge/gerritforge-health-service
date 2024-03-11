#!/bin/bash

echo "The top #10 projects in terms of updates of 2024:"
echo "================================================="
zgrep INFO sharedref_log.2024*gz | \
    sed -e 's/INFO/|/g' | grep -v 'All-Users' | \
    cut -d '|' -f 2- | cut -d ':' -f 2- | jq -r '.project_name' | \
    sed -e 's/\.git//g' | sort | uniq -c | sort -r -n | head -10

echo "The top #10 projects in terms of upload-packs of 2024:"
echo "======================================================"
{ zgrep git-upload-pack sshd_log.2024*gz | \
    sed -e 's/git-upload-pack/|/g' | grep -v 'All-Users' | \
    cut -d '|' -f 2- | awk '{print $1}' | \
    sed -e 's/\.git//g'; \
  zgrep git-upload-pack httpd_log.2024*gz | grep POST | grep -v 401 | \
    sed -e 's/POST/|/g' | grep -v 'All-Users' | \
    cut -d '|' -f 2- | sed -e 's/git-upload-pack/|/g' | cut -d '|' -f 1 | tr -d ' ' | \
    sed -e 's/^\///g' | sed -e 's/\/$//g' | sed -e 's/^a\///g' | \
    sed -e 's/\.git//g'; } | \
    sort | uniq -c | sort -r -n | head -10