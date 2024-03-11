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
python3 scrape.py http://localhost:8080/plugins/metrics-reporter-prometheus/metrics --bearer-token token --output-csv-file /tmp/metrics.csv
```

### pipenv

```bask
python scrape.py http://localhost:8080/plugins/metrics-reporter-prometheus/metrics --bearer-token token --output-csv-file /tmp/metrics.csv
```
