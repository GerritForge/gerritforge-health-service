## Dependencies

* python3
* virtualenv

## Prepare the environment

### Create virtual env (if you don't have already)

```bash
virtualenv -p python3 ghs-prometheus-consumer
```

### Activate virtual env

```bash
 source ghs-prometheus-consumer/bin/activate
```

### Install requirements (if you don't have already)

```bash
pip3 install -r requirements.txt
```

### Deactivate virtual env

```bash
deactivate
```

## How to run it

```bash
python3 scrape.py http://localhost:8080/plugins/metrics-reporter-prometheus/metrics --token token --output-csv-file /tmp/metrics.csv
```
