
## Docker

### Build

```
docker build -f ghs-noaction-model/Dockerfile -t gerritforge/ghs-noaction-model:$(git rev-parse --short HEAD) .
```

### Build and push multi-platform

```
docker buildx build -f ghs-noaction-model/Dockerfile --push --platform linux/arm64/v8,linux/amd64 -t gerritforge/ghs-noaction-model:$(git rev-parse --short HEAD) .
```

### Run

```
docker run docker.io/gerritforge/ghs-noaction-model:<tag>
```
