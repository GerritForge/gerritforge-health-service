#!/bin/bash

export REPO=cue-lang/cue

echo "Most common scenarios of updating project $1"
echo "============================================"
zgrep $REPO sharedref_log.2024*gz | sed -e 's/ \/a/ /g' | \
      cut -d ']' -f 2 | cut -d '[' -f 2 | sed -e 's/ReceiveCommits.*/ReceiveCommits/g' | \
      cut -d '(' -f 1 | sed -e 's/%2F/\//g' | sed -e 's/[0-9]/N/g' | sed -e 's/\/NN\//\/N\//g' | sort | uniq -c | \
      sort -n -r | head -10