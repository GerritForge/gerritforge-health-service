
## Docker

### Build

```
docker build -f ghs-dummy-q-model/Dockerfile -t gerritforge/ghs-q-model:latest .
```

### Run

```
docker run -v <git repository path>:/git/gerrit.git docker.io/gerritforge/ghs-q-model:latest
```