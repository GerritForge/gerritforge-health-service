# How to run the experiment locally

## Setup gerrit

### Create Gerrit site

```bash
mkdir -p gerrit/plugins
mkdir -p gerrit/etc
```

### Download all Gerrit related components:

```bash
wget https://gerrit-ci.gerritforge.com/view/Gerrit/job/Gerrit-bazel-stable-3.9/lastSuccessfulBuild/artifact/gerrit/bazel-bin/release.war -O gerrit.war
wget https://gerrit-ci.gerritforge.com/view/Plugins-stable-3.9/job/plugin-metrics-reporter-prometheus-bazel-master-stable-3.9/lastSuccessfulBuild/artifact/bazel-bin/plugins/metrics-reporter-prometheus/metrics-reporter-prometheus.jar -O gerrit/plugins/metrics-reporter-prometheus.jar
wget https://gerrit-ci.gerritforge.com/view/Plugins-stable-3.9/job/plugin-git-repo-metrics-bazel-master-stable-3.9/lastSuccessfulBuild/artifact/bazel-bin/plugins/git-repo-metrics/git-repo-metrics.jar -O gerrit/plugins/git-repo-metrics.jar
# TODO create CI action to build gerrit-per-repo-metrics-collector.jar plugin so that it could be downloaded
```

### Start Gerrit site

#### Configuration

Note that `repo` needs to be switched to repository name that wants to be worked on.

```bash
git config --file gerrit/etc/gerrit.config gerrit.basePath git
git config --file gerrit/etc/gerrit.config gerrit.instanceId 1
git config --file gerrit/etc/gerrit.config auth.type DEVELOPMENT_BECOME_ANY_ACCOUNT
git config --file gerrit/etc/gerrit.config sendemail.enable false
git config --file gerrit/etc/gerrit.config auth.httpPasswordSettingsEnabled true
git config --file gerrit/etc/gerrit.config container.user $(whoami)
git config --file gerrit/etc/gerrit.config sshd.listenAddress "*:29418"
git config --file gerrit/etc/gerrit.config httpd.listenUrl "http://*:8080/"
git config --file gerrit/etc/gerrit.config plugins.allowRemoteAdmin true
git config --file gerrit/etc/gerrit.config plugin."gerrit-per-repo-metrics-collector".uploadPackMetricsRepo repo
git config --file gerrit/etc/gerrit.config plugin."metrics-reporter-prometheus".prometheusBearerToken token

git config --file gerrit/etc/git-repo-metrics.config git-repo-metrics.project repo
git config --file gerrit/etc/git-repo-metrics.config git-repo-metrics.gracePeriod 1m
```

#### Start the site locally

> Ensure that JDK 17 is in your path

```bash
java -jar gerrit.war init --install-plugin download-commands -d gerrit --batch # init the site
gerrit/bin/gerrit.sh start # start the site
```

Ewentually it should start without errors and claim that it is ready:

```bash
tail -f gerrit/logs/error_log
...
[2024-03-15T14:18:57.918Z] [main] INFO  org.eclipse.jetty.server.Server : Started @3756ms
[2024-03-15T14:18:57.920Z] [main] INFO  com.google.gerrit.pgm.Daemon : Gerrit Code Review 3.9.2-3-g6ecb753861 ready
```

Create the `repo` and ensure that it was clonned/modified (changes pushed for review, etc.) so that prometheus
[endpoint](http://localhost:8080/plugins/metrics-reporter-prometheus/metrics) exposes the following metrics:

```bash
plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_bitmap_index_misses_repo -1.0
plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_phase_searching_for_reuse_repo 1.0

plugins_git_repo_metrics_combinedrefssha1_repo 1.6711706E7
plugins_git_repo_metrics_numberofbitmaps_repo 0.0
plugins_git_repo_metrics_numberofdirectories_repo 13.0
plugins_git_repo_metrics_numberofemptydirectories_repo 1.0
plugins_git_repo_metrics_numberoffiles_repo 14.0
plugins_git_repo_metrics_numberofkeepfiles_repo 0.0
plugins_git_repo_metrics_numberoflooseobjects_repo 10.0
plugins_git_repo_metrics_numberoflooserefs_repo 3.0
plugins_git_repo_metrics_numberofpackedobjects_repo 30.0
plugins_git_repo_metrics_numberofpackedrefs_repo 10.0
plugins_git_repo_metrics_numberofpackfiles_repo 2.0
plugins_git_repo_metrics_sizeoflooseobjects_repo 2459.0
plugins_git_repo_metrics_sizeofpackedobjects_repo 2459.0

proc_cpu_num_cores 10.0
proc_cpu_system_load 2.892578125
proc_cpu_usage 14.034397
```

## Get model components

Pull the corresponding docker images - navigate to the dockerhub
[ghs-q-model](https://hub.docker.com/r/gerritforge/ghs-q-model/tags) and selecte the version that you are
interested in (note that there is no latest)

```bash
docker pull gerritforge/ghs-q-model:[sha1]
docker pull gerritforge/ghs-gerrit-scraper:[sha1] # optional if one wants to run scraper in batch mode
```

## Executing the model

### Provide the necessary configuration

Consult the configuration [template](https://review.gerrithub.io/plugins/gitiles/GerritForge/gerritforge-health-service/+/refs/heads/master/components/ghs-dummy-q-model/config.ini.template)
for all variables that needs to be provided.

Here is the example of the `docker-compose.yaml`:

```yaml
version: '3'

services:
  ghs-q-model:
    image: gerritforge/ghs-q-model:120a002
    volumes:
      - ./q-model-output:/tmp
      - ./gerrit/git/GerritForge/ghs-gym.git:/git/GerritForge/test-repo.git
    environment:
      - Q_LEARN_GERRIT_URL=host.docker.internal:8080
      - Q_LEARN_BEARER_TOKEN=token
      - Q_LEARN_GIT_REPO=test-repo
      - Q_LEARN_NUM_EPISODES=20
      - Q_LEARN_USERNAME=admin
      - Q_LEARN_PASSWORD=secret
      - Q_LEARN_EPSILON=0.7
```

Start it with:

```bash
docker compose up
```

When everything works it will run 20 episodes and finish with:

```bash
[+] Running 1/0
 ✔ Container tmp-ghs-q-model-1  Recreated
Attaching to ghs-q-model-1
ghs-q-model-1  | 2024-03-15 16:45:33,078 - INFO - action taken by model: 2
ghs-q-model-1  | 2024-03-15 16:45:33,091 - INFO - executing action PackRefsAction, episode number 1
ghs-q-model-1  | 2024-03-15 16:45:33,254 - INFO - action PackRefsAction executed successfuly
ghs-q-model-1  | 2024-03-15 16:45:33,499 - INFO - step executed successfuly. Result:1,-1.0,0.3,0.1,-1.0,0.3,0.1,2,0.26666666666666666
ghs-q-model-1  | 2024-03-15 16:45:33,502 - INFO - reward generated for action: 2, reward:0
...
ghs-q-model-1  | 2024-03-15 16:45:39,411 - INFO - action taken by model: 1
ghs-q-model-1  | 2024-03-15 16:45:39,424 - INFO - executing action BitmapGenerationAction, episode number 20
ghs-q-model-1  | 2024-03-15 16:45:39,601 - INFO - action BitmapGenerationAction executed successfuly
ghs-q-model-1  | 2024-03-15 16:45:39,795 - INFO - step executed successfuly. Result:20,-1.0,0.3,0.1,-1.0,0.3,0.1,1,0.0
ghs-q-model-1  | 2024-03-15 16:45:39,796 - INFO - reward generated for action: 1, reward:0
ghs-q-model-1 exited with code 0
```

One can examine the outputs:

Q-function:
```bash
$ cat q-model-output/q_status_1710521133.059283.json | jq
{
  "[-1.0, 0.3, 0.1]": [
    0.4685571411463505,
    0.08969312292198517,
    0.08494459821474777
  ]
}
```

Model stats:
```bash
$ tail -f q-model-output/state_dump_1710521133.056244.csv
11,-1.0,0.3,0.1,-1.0,0.3,0.1,0,0.3333333333333333
12,-1.0,0.3,0.1,-1.0,0.3,0.1,0,0.3333333333333333
13,-1.0,0.3,0.1,-1.0,0.3,0.1,0,0.3333333333333333
14,-1.0,0.3,0.1,-1.0,0.3,0.1,0,0.3333333333333333
15,-1.0,0.3,0.1,-1.0,0.3,0.1,1,0.0
16,-1.0,0.3,0.1,-1.0,0.3,0.1,2,0.26666666666666666
17,-1.0,0.3,0.1,-1.0,0.3,0.1,0,0.3333333333333333
18,-1.0,0.3,0.1,-1.0,0.3,0.1,0,0.3333333333333333
19,-1.0,0.3,0.1,-1.0,0.3,0.1,0,0.3333333333333333
20,-1.0,0.3,0.1,-1.0,0.3,0.1,1,0.0
```
