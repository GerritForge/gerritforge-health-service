## Dependencies

* python3
* virtualenv (alternatively `pipenv`)

## Prepare the environment

### viertualenv

#### Create virtual env (if you don't have already)

```bash
virtualenv -p python3 ghs-prometheus-consumer
```

#### Activate virtual env

```bash
 source ghs-prometheus-consumer/bin/activate
```

#### Install requirements (if you don't have already)

```bash
pip3 install -r requirements.txt
```

#### Deactivate virtual env

```bash
deactivate
```

### pipenv

#### Crate the virtual env and install dependencies

```bash
pipenv install -python 3 -r requirements.txt
```

#### Activete the vietual env

```bash
pipenv shell
```

#### Deactive the vritual env

Either press `ctrl(cmd) + d` or
```bash
exit
```

## How to run it

### virtualenv

```bash
python3 scrape.py http://localhost:8080/plugins/metrics-reporter-prometheus/metrics --repository test-repo --bearer-token token --output-csv-file /tmp/metrics.csv
```

### pipenv

```bash
python scrape.py http://localhost:8080/plugins/metrics-reporter-prometheus/metrics --repository test-repo --bearer-token token --output-csv-file /tmp/metrics.csv
```

### snapshot mode

By default `scraper` runs in _batch_ mode which means that it will keep appending rows to the `--output-csv-` file.
However it also be called in the _snapshot_ mode where it would just output the metrics snapshot as JSON.

```bash
python scrape.py http://localhost:8080/plugins/metrics-reporter-prometheus/metrics --mode snapshot --repository test-repo --bearer-token token
{
  "plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_bitmap_index_misses_test_repo": 15.0,
  "plugins_gerrit_per_repo_metrics_collector_ghs_git_upload_pack_phase_searching_for_reuse_test_repo": 4.0,
  "plugins_git_repo_metrics_combinedrefssha1_test_repo": 135.0,
  "plugins_git_repo_metrics_numberofbitmaps_test_repo": 7.0,
  "plugins_git_repo_metrics_numberofdirectories_test_repo": 3.0,
  "plugins_git_repo_metrics_numberofemptydirectories_test_repo": 1.0,
  "plugins_git_repo_metrics_numberoffiles_test_repo": 18.0,
  "plugins_git_repo_metrics_numberofkeepfiles_test_repo": 0.0,
  "plugins_git_repo_metrics_numberoflooseobjects_test_repo": 0.0,
  "plugins_git_repo_metrics_numberoflooserefs_test_repo": 2.0,
  "plugins_git_repo_metrics_numberofpackedobjects_test_repo": 100.0,
  "plugins_git_repo_metrics_numberofpackedrefs_test_repo": 1.0,
  "plugins_git_repo_metrics_numberofpackfiles_test_repo": 8.0,
  "plugins_git_repo_metrics_sizeoflooseobjects_test_repo": 0.0,
  "plugins_git_repo_metrics_sizeofpackedobjects_test_repo": 7074.0,
  "proc_cpu_num_cores": 10.0,
  "proc_cpu_system_load": 2.56787109375,
  "proc_cpu_usage": 148.09181,
  "timestamp": 1710284380
}
```
