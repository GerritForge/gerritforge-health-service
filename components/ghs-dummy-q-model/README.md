
## Docker

### Build

```
docker build -f ghs-dummy-q-model/Dockerfile -t gerritforge/ghs-q-model:$(git rev-parse --short HEAD) .
```

### Build and push multi-platform

```
docker buildx build -f ghs-dummy-q-model/Dockerfile --push --platform linux/arm64/v8,linux/amd64 -t gerritforge/ghs-q-model:$(git rev-parse --short HEAD) .
```

### Run

```
docker run -v <git repository path>:/git/gerrit.git docker.io/gerritforge/ghs-q-model:<tag>
```
